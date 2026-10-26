import { useEffect, useLayoutEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent, type PointerEvent as ReactPointerEvent } from "react";
import { createPortal } from "react-dom";
import type { Player, Rotation, Team } from "../../engine/types";
import { mutate, useLeague } from "../store";
import { roster, team } from "../../engine/core";
import { classLabel } from "../../engine/ratings";
import { autoRotation } from "../../engine/sim/rotation";
import { availablePlayers } from "../../engine/play";
import { Card, Grade, PageHead, PlayerLink } from "../components/common";
import { seasonStatsOf } from "../helpers";
import { StatusBadges } from "./Roster";

// The depth chart is one ordered list: the top five start, and each spot keeps its minutes, so dragging the
// sixth man up to the top hands him the starter's minutes (and the starter takes his). Anyone at 0 is out
// of the rotation. Injured and redshirting players sit in their own list and keep their spot for when
// they're back.

const MAX_MIN = 40;

type Auto = ReturnType<typeof autoRotation>;

/** Available players in depth-chart order. */
function depthOrder(rot: Rotation, avail: Player[], auto: Auto): Player[] {
  const minutes = rot.auto ? auto.minutes : rot.minutes;
  const starters = rot.auto ? auto.starters : rot.starters;
  const byMinutes = (a: Player, b: Player) => (minutes[b.id] ?? 0) - (minutes[a.id] ?? 0) || b.ovr - a.ovr;
  const saved = rot.auto ? [] : (rot.order ?? []);
  const ids = new Set(avail.map((p) => p.id));
  const out: Player[] = [];
  const seen = new Set<number>();
  const take = (id: number) => {
    if (!ids.has(id) || seen.has(id)) return;
    seen.add(id);
    out.push(avail.find((p) => p.id === id)!);
  };
  saved.forEach(take);
  // older saves (and auto) have no order: starters first, then by minutes
  if (!saved.length) avail.filter((p) => starters.includes(p.id)).sort(byMinutes).forEach((p) => take(p.id));
  avail.slice().sort(byMinutes).forEach((p) => take(p.id));
  return out;
}

/** Hand the rotation to the user, starting from what auto would do. */
function ensureManual(t: Team, avail: Player[], everyone: Player[], auto: Auto) {
  if (!t.rotation.auto) return;
  const order = depthOrder(t.rotation, avail, auto).map((p) => p.id);
  t.rotation = { auto: false, starters: order.slice(0, 5), minutes: { ...auto.minutes }, order: [...order, ...everyone.filter((p) => !order.includes(p.id)).map((p) => p.id)] };
}

/** Save a new order of the available players; unavailable ones keep their places in the full chart. */
function saveOrder(t: Team, next: number[], everyone: Player[], availIds: Set<number>) {
  const rot = t.rotation;
  const full = rot.order?.filter((id) => everyone.some((p) => p.id === id)) ?? [];
  for (const p of everyone) if (!full.includes(p.id)) full.push(p.id);
  const queue = next.slice();
  rot.order = full.map((id) => (availIds.has(id) ? queue.shift()! : id));
  rot.starters = rot.order.filter((id) => availIds.has(id)).slice(0, 5);
}

function Grip() {
  return (
    <svg width="12" height="18" viewBox="0 0 12 18" aria-hidden>
      {[3, 9, 15].flatMap((y) => [3, 9].map((x) => <circle key={`${x}-${y}`} cx={x} cy={y} r="1.6" fill="currentColor" />))}
    </svg>
  );
}

/** − 34 + with press-and-hold. */
function MinuteStepper({ v, onChange, disabled }: { v: number; onChange: (v: number) => void; disabled?: boolean }) {
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cur = useRef(v);
  cur.current = v;
  const stop = () => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
  };
  useEffect(() => stop, []);
  const press = (d: number) => (e: ReactPointerEvent) => {
    e.preventDefault();
    const step = () => onChange(Math.max(0, Math.min(MAX_MIN, cur.current + d)));
    step();
    const repeat = (delay: number) => {
      timer.current = setTimeout(() => {
        step();
        repeat(70);
      }, delay);
    };
    repeat(380);
  };
  return (
    <div className="rot-step">
      <button type="button" disabled={disabled || v <= 0} onPointerDown={press(-1)} onPointerUp={stop} onPointerLeave={stop} onPointerCancel={stop} aria-label="Fewer minutes">
        −
      </button>
      <span className="num">{v}</span>
      <button type="button" disabled={disabled || v >= MAX_MIN} onPointerDown={press(1)} onPointerUp={stop} onPointerLeave={stop} onPointerCancel={stop} aria-label="More minutes">
        +
      </button>
    </div>
  );
}

const GROUP: Record<string, "G" | "W" | "B"> = { PG: "G", SG: "G", SF: "W", PF: "B", C: "B" };

/** "2 guards · 1 wing · 2 bigs", and a word of warning from the staff if it's lopsided. */
function lineupNote(ps: Player[]): { text: string; warn: string | null } {
  const n = { G: 0, W: 0, B: 0 };
  for (const p of ps) n[GROUP[p.pos]]++;
  const part = (k: number, one: string, many: string) => (k ? `${k} ${k === 1 ? one : many}` : null);
  const text = [part(n.G, "guard", "guards"), part(n.W, "wing", "wings"), part(n.B, "big", "bigs")].filter(Boolean).join(" · ");
  const warn = !n.G ? "No guards: nobody to bring the ball up" : !n.B ? "No bigs: you'll get beat on the glass" : n.B >= 4 ? "Four bigs: crowded floor, not much shooting" : null;
  return { text, warn };
}

interface DragState {
  pid: number;
  from: number;
  to: number;
  /** where the floating copy sits, in the viewport */
  x: number;
  y: number;
  w: number;
}

interface Live {
  pid: number;
  from: number;
  to: number;
  startX: number;
  startY: number;
  lastY: number;
  started: boolean;
  /** where on the row it was grabbed, and the row's size */
  grab: number;
  h: number;
  x: number;
  w: number;
  /** the middle of each spot as laid out when the drag began (list coordinates) */
  mids: number[];
  scroller: HTMLElement;
  raf: number;
}

function moved<T>(xs: T[], from: number, to: number): T[] {
  const out = xs.slice();
  const [x] = out.splice(from, 1);
  out.splice(to, 0, x);
  return out;
}

function scrollerOf(el: HTMLElement): HTMLElement {
  for (let n = el.parentElement; n; n = n.parentElement) {
    const o = getComputedStyle(n).overflowY;
    if ((o === "auto" || o === "scroll") && n.scrollHeight > n.clientHeight) return n;
  }
  return (document.scrollingElement as HTMLElement) ?? document.documentElement;
}

export function RotationPage() {
  const L = useLeague();
  const t = team(L, L.userTid);
  const all = roster(L, t.id);
  const avail = availablePlayers(L, t.id);
  const availIds = new Set(avail.map((p) => p.id));
  const out = all.filter((p) => !availIds.has(p.id));
  const auto = autoRotation(avail);
  const rot = t.rotation;
  const minutes = rot.auto ? auto.minutes : rot.minutes;
  const order = depthOrder(rot, avail, auto);
  const total = order.reduce((a, p) => a + (minutes[p.id] ?? 0), 0);
  // each spot's minutes: whoever lands in a spot plays them
  const spotMin = order.map((p) => minutes[p.id] ?? 0);

  const [drag, setDrag] = useState<DragState | null>(null);
  const [picked, setPicked] = useState<number | null>(null);
  // while dragging, the list shows where everyone would end up
  const view = drag ? moved(order, drag.from, drag.to) : order;
  const note = lineupNote(view.slice(0, 5));

  // ---- editing ----
  const reorder = (ids: number[]) =>
    mutate(() => {
      ensureManual(t, avail, all, auto);
      const spot = order.map((p) => t.rotation.minutes[p.id] ?? 0);
      ids.forEach((pid, i) => (t.rotation.minutes[pid] = spot[i]));
      saveOrder(t, ids, all, availIds);
    });
  const move = (from: number, to: number) => {
    if (from === to || to < 0 || to >= order.length) return;
    reorder(moved(order, from, to).map((p) => p.id));
  };
  const swap = (a: number, b: number) => {
    if (a === b || a < 0 || b < 0) return;
    const ids = order.map((p) => p.id);
    [ids[a], ids[b]] = [ids[b], ids[a]];
    reorder(ids);
  };
  /** Click one player, then another, and they trade places (and minutes). */
  const pick = (pid: number) => {
    if (picked === null) return setPicked(pid);
    setPicked(null);
    if (picked !== pid) swap(order.findIndex((p) => p.id === picked), order.findIndex((p) => p.id === pid));
  };
  useEffect(() => {
    if (picked === null) return;
    const k = (e: KeyboardEvent) => e.key === "Escape" && setPicked(null);
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [picked]);
  const setMin = (pid: number, v: number) =>
    mutate(() => {
      ensureManual(t, avail, all, auto);
      t.rotation.minutes[pid] = Math.max(0, Math.min(MAX_MIN, Math.round(v)));
    });
  const scaleTo200 = () =>
    mutate(() => {
      const ids = order.map((p) => p.id);
      let sum = ids.reduce((a, id) => a + (t.rotation.minutes[id] ?? 0), 0);
      if (sum <= 0) return;
      for (const id of ids) t.rotation.minutes[id] = Math.min(MAX_MIN, Math.round(((t.rotation.minutes[id] ?? 0) * 200) / sum));
      sum = ids.reduce((a, id) => a + (t.rotation.minutes[id] ?? 0), 0);
      // whatever rounding leaves over goes to (or comes from) the biggest roles
      const big = ids.slice().sort((a, b) => (t.rotation.minutes[b] ?? 0) - (t.rotation.minutes[a] ?? 0));
      for (let i = 0, guard = 0; sum !== 200 && guard < 400; i = (i + 1) % big.length, guard++) {
        const id = big[i];
        const m = t.rotation.minutes[id] ?? 0;
        if (sum < 200 && m < MAX_MIN) {
          t.rotation.minutes[id] = m + 1;
          sum++;
        } else if (sum > 200 && m > 0) {
          t.rotation.minutes[id] = m - 1;
          sum--;
        }
      }
    });
  const takeManual = () =>
    mutate(() => {
      const ids = depthOrder({ auto: true, starters: [], minutes: {} }, avail, auto).map((p) => p.id);
      t.rotation = { auto: false, starters: ids.slice(0, 5), minutes: { ...auto.minutes }, order: [...ids, ...out.map((p) => p.id)] };
    });

  // ---- moving rows smoothly: whenever the order changes, each row glides from where it was ----
  const listRef = useRef<HTMLDivElement>(null);
  const tops = useRef(new Map<number, number>());
  const lastKey = useRef("");
  const landFrom = useRef<{ pid: number; top: number } | null>(null);
  const viewKey = view.map((p) => p.id).join(",");
  useLayoutEffect(() => {
    const box = listRef.current;
    if (!box) return;
    const changed = lastKey.current !== "" && lastKey.current !== viewKey;
    lastKey.current = viewKey;
    const land = landFrom.current;
    landFrom.current = null;
    for (const el of box.querySelectorAll<HTMLElement>("[data-pid]")) {
      const pid = Number(el.dataset.pid);
      const top = el.offsetTop;
      const prev = tops.current.get(pid);
      tops.current.set(pid, top);
      let from: number | null = null;
      if (land?.pid === pid) from = land.top - top;
      else if (changed && prev !== undefined && prev !== top) {
        // start from where it is on screen right now, even halfway through another glide
        const tf = getComputedStyle(el).transform;
        from = prev + (tf && tf !== "none" ? new DOMMatrixReadOnly(tf).m42 : 0) - top;
      }
      if (from === null) continue;
      el.style.transition = "none";
      el.style.transform = `translateY(${from}px)`;
      void el.offsetHeight;
      el.style.transition = "transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1)";
      el.style.transform = "";
    }
  });

  // ---- dragging (mouse, touch and pen through pointer events) ----
  const live = useRef<Live | null>(null);
  const justDragged = useRef(false);
  const update = () => {
    const d = live.current;
    const box = listRef.current;
    if (!d || !box || !d.started) return;
    // the spot nearest the middle of the floating row
    const center = d.lastY - d.grab + d.h / 2 - box.getBoundingClientRect().top;
    let to = d.from;
    let best = Infinity;
    d.mids.forEach((m, i) => {
      if (Math.abs(m - center) < best) {
        best = Math.abs(m - center);
        to = i;
      }
    });
    d.to = to;
    setDrag({ pid: d.pid, from: d.from, to, x: d.x, y: d.lastY - d.grab, w: d.w });
  };
  const tick = () => {
    const d = live.current;
    if (!d) return;
    // near the top or bottom edge, scroll the page along
    const edge = 70;
    const r = d.scroller === document.scrollingElement ? { top: 0, bottom: window.innerHeight } : d.scroller.getBoundingClientRect();
    const v = d.lastY < r.top + edge ? -Math.ceil((r.top + edge - d.lastY) / 6) : d.lastY > r.bottom - edge ? Math.ceil((d.lastY - (r.bottom - edge)) / 6) : 0;
    if (v) {
      d.scroller.scrollTop += v;
      update();
    }
    d.raf = requestAnimationFrame(tick);
  };
  const begin = (d: Live) => {
    const box = listRef.current!;
    const els = [...box.querySelectorAll<HTMLElement>("[data-pid]")].sort((a, b) => a.offsetTop - b.offsetTop);
    d.mids = els.map((el) => el.offsetTop + el.offsetHeight / 2);
    const r = els.find((el) => Number(el.dataset.pid) === d.pid)!.getBoundingClientRect();
    Object.assign(d, { started: true, grab: d.startY - r.top, h: r.height, x: r.left, w: r.width });
    setPicked(null);
    document.body.classList.add("dragging-row");
    d.raf = requestAnimationFrame(tick);
  };
  const onGripDown = (i: number, pid: number) => (e: ReactPointerEvent<HTMLButtonElement>) => {
    if (e.button !== 0) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    live.current = { pid, from: i, to: i, startX: e.clientX, startY: e.clientY, lastY: e.clientY, started: false, grab: 0, h: 0, x: 0, w: 0, mids: [], scroller: scrollerOf(e.currentTarget), raf: 0 };
  };
  const onGripMove = (e: ReactPointerEvent) => {
    const d = live.current;
    if (!d) return;
    d.lastY = e.clientY;
    // a few pixels of movement makes it a drag; otherwise it's a click (which picks him for a swap)
    if (!d.started && Math.hypot(e.clientX - d.startX, e.clientY - d.startY) > 5) begin(d);
    update();
  };
  const finish = (commit: boolean) => {
    const d = live.current;
    live.current = null;
    if (!d?.started) return;
    cancelAnimationFrame(d.raf);
    document.body.classList.remove("dragging-row");
    justDragged.current = true;
    setTimeout(() => (justDragged.current = false), 0);
    // settle into the spot from wherever it was let go
    const box = listRef.current;
    if (box) landFrom.current = { pid: d.pid, top: d.lastY - d.grab - box.getBoundingClientRect().top };
    lastKey.current = "";
    setDrag(null);
    if (commit) move(d.from, d.to);
  };
  useEffect(
    () => () => {
      if (live.current) cancelAnimationFrame(live.current.raf);
      document.body.classList.remove("dragging-row");
    },
    [],
  );
  const onGripKey = (i: number) => (e: ReactKeyboardEvent<HTMLButtonElement>) => {
    const d = e.key === "ArrowUp" ? -1 : e.key === "ArrowDown" ? 1 : 0;
    if (!d) return;
    e.preventDefault();
    move(i, i + d);
    // keep focus on the same player as he moves
    const pid = order[i].id;
    requestAnimationFrame(() => listRef.current?.querySelector<HTMLButtonElement>(`[data-grip="${pid}"]`)?.focus());
  };

  const pickedPlayer = picked === null ? null : (order.find((p) => p.id === picked) ?? null);
  const pressedControl = useRef(false);

  /** One player's row; `ghost` is the copy that floats under the pointer. */
  const row = (p: Player, i: number, ghost = false, slot?: number) => {
    const m = drag ? spotMin[i] : (minutes[p.id] ?? 0);
    const s = seasonStatsOf(p, L.season, t.id);
    const role = i < 5 ? "Starter" : m > 0 ? (i === 5 ? "6th man" : "Bench") : "Out of rotation";
    const cls = `rot-row${i < 5 ? " starter" : ""}${m === 0 ? " dnp" : ""}${!ghost && drag?.pid === p.id ? " placeholder" : ""}${picked === p.id ? " picked" : ""}`;
    return (
      <div
        key={p.id}
        data-pid={ghost ? undefined : p.id}
        className={cls}
        style={slot === undefined ? undefined : { order: slot }}
        onPointerDown={ghost ? undefined : (e) => (pressedControl.current = !!(e.target as HTMLElement).closest("a, input, .rot-step"))}
        onClick={
          ghost
            ? undefined
            : (e) => {
                const el = e.target as HTMLElement;
                if (pressedControl.current || el.closest("a, input, .rot-step") || (el.closest(".rot-grip") && justDragged.current)) return;
                pick(p.id);
              }
        }
      >
        {ghost ? (
          <span className="rot-grip">
            <Grip />
          </span>
        ) : (
          <button type="button" className="rot-grip" data-grip={p.id} onPointerDown={onGripDown(i, p.id)} onPointerMove={onGripMove} onPointerUp={() => finish(true)} onPointerCancel={() => finish(false)} onLostPointerCapture={() => finish(true)} onKeyDown={onGripKey(i)} aria-label={`Move ${p.first} ${p.last}: drag, use the arrow keys, or press to pick him for a swap`} title="Drag to move, or click to swap">
            <Grip />
          </button>
        )}
        <span className="rot-n">{i + 1}</span>
        <div className="rot-player">
          <PlayerLink
            L={L}
            p={p}
            face
            size={28}
            colors={t.colors}
            meta={
              <>
                {p.pos} · {classLabel(p)} · {role}
                {s && s.g > 0 && <> · {(s.min / s.g).toFixed(1)} mpg</>}
              </>
            }
          />
          <StatusBadges L={L} p={p} />
        </div>
        <span className="rot-ovr">
          <Grade v={p.ovr} />
        </span>
        <input className="rot-slider" type="range" min={0} max={MAX_MIN} value={m} onChange={(e) => setMin(p.id, Number(e.target.value))} aria-label={`Minutes for ${p.first} ${p.last}`} />
        <MinuteStepper v={m} onChange={(v) => setMin(p.id, v)} />
      </div>
    );
  };

  return (
    <div>
      <PageHead
        title="Rotation"
        sub="Drag players into order: the top five start, and each spot keeps its minutes. In games, the coach subs toward these minutes, around fatigue and foul trouble, and goes to the best five late in close games."
        right={
          <label className="check nowrap">
            <input type="checkbox" checked={rot.auto} onChange={(e) => (e.target.checked ? mutate(() => void (t.rotation = { auto: true, starters: [], minutes: {} })) : takeManual())} />
            Auto rotation
          </label>
        }
      />
      <div className="rot-layout">
        <Card
          title="Depth chart"
          sub="Drag the handle to move a player, or click two players to swap them. Drop a player at the bottom to sit him."
          flush
          right={
            <div className="row">
              <span className={`badge ${total === 200 ? "good" : "bad"}`} title="A game has 200 player-minutes (5 players × 40)">
                {total} / 200 min
              </span>
              {/* always there, so the header doesn't jump when it's needed */}
              <button className="btn btn-sm" onClick={scaleTo200} disabled={rot.auto || total === 200}>
                Scale to 200
              </button>
            </div>
          }
        >
          <div className={`rot-list${picked !== null ? " picking" : ""}`} ref={listRef}>
            <div className="rot-sec" style={{ order: 0 }}>
              <b>Starting five</b>
              <span className="faint">{note.text}</span>
              {note.warn && <span className="badge warn">{note.warn}</span>}
            </div>
            {view.length > 5 && (
              <div className="rot-sec" style={{ order: 6 }}>
                <b>Bench</b>
                <span className="faint">If a starter is hurt, the first one here at his position starts</span>
              </div>
            )}
            {/* rows stay in saved order in the page; while dragging only their on-screen order changes, so the row being dragged is never rebuilt */}
            {order.map((p) => {
              const i = view.indexOf(p);
              return row(p, i, false, i < 5 ? i + 1 : i + 2);
            })}
          </div>
          {drag &&
            createPortal(
              <div className="rot-ghost" style={{ left: drag.x, top: drag.y, width: drag.w }}>
                {row(order[drag.from], drag.to, true)}
              </div>,
              document.body,
            )}
          {/* room to scroll any row clear of the swap prompt */}
          {pickedPlayer && <div style={{ height: 72 }} />}
          {pickedPlayer &&
            createPortal(
              <div className="rot-swapbar" role="status">
                <span>
                  Swap <b>{pickedPlayer.first[0]}. {pickedPlayer.last}</b> with… pick another player
                </span>
                <button className="btn btn-sm" onClick={() => setPicked(null)}>
                  Cancel
                </button>
              </div>,
              document.body,
            )}
          {out.length > 0 && (
            <div className="rot-out">
              <div className="rot-sec">
                <b>Unavailable</b>
                <span className="faint">They keep their spot on the chart for when they're back</span>
              </div>
              {out.map((p) => (
                <div key={p.id} className="rot-row out">
                  <span />
                  <span className="rot-n" />
                  <div className="rot-player">
                    <PlayerLink L={L} p={p} face size={28} colors={t.colors} meta={`${p.pos} · ${classLabel(p)}`} />
                    <StatusBadges L={L} p={p} />
                  </div>
                  <span className="rot-ovr">
                    <Grade v={p.ovr} />
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>
        <div className="col gap-16">
          <Card title="How rotations work">
            <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.6 }}>
              <li>Drag a player by the handle, or click one player and then another to swap them (arrow keys work on a focused handle). Each spot keeps its minutes, so moving your sixth man into the top five hands him a starter's minutes.</li>
              <li>Starters open each half.</li>
              <li>Players tire on the floor and recover on the bench; tired players perform worse.</li>
              <li>Two first-half fouls or four second-half fouls send a player to the bench.</li>
              <li>Blowouts empty the bench; close games late go to your best five.</li>
              <li>If a starter is hurt, the next man down the chart at his position starts, and his minutes are shared out.</li>
            </ul>
          </Card>
          {!rot.auto && (
            <Card title="Auto suggestion">
              <div className="small muted mb-8">The auto rotation would start:</div>
              <div className="col gap-4">
                {auto.starters.map((id) => {
                  const p = all.find((x) => x.id === id)!;
                  return (
                    <div key={id} className="row small">
                      <span style={{ width: 26 }}>{p.pos}</span>
                      <span style={{ flex: 1 }}>
                        {p.first} {p.last}
                      </span>
                      <span className="muted">{auto.minutes[id]} min</span>
                    </div>
                  );
                })}
              </div>
              <button className="btn btn-sm mt-12" onClick={takeManual}>
                Reset to suggestion
              </button>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
