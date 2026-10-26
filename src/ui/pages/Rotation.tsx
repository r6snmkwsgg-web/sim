import { useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent, type PointerEvent as ReactPointerEvent } from "react";
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

interface Drag {
  pid: number;
  from: number;
  to: number;
  dy: number;
  line: number | null;
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
  const starters = order.slice(0, 5);
  const note = lineupNote(starters);

  // ---- editing ----
  const move = (from: number, to: number) => {
    if (from === to || to < 0 || to >= order.length) return;
    mutate(() => {
      ensureManual(t, avail, all, auto);
      const ids = order.map((p) => p.id);
      // each spot keeps its minutes: whoever lands there plays them
      const spotMin = ids.map((id) => t.rotation.minutes[id] ?? 0);
      const [id] = ids.splice(from, 1);
      ids.splice(to, 0, id);
      ids.forEach((pid, i) => (t.rotation.minutes[pid] = spotMin[i]));
      saveOrder(t, ids, all, availIds);
    });
  };
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

  // ---- dragging (mouse, touch and pen through pointer events) ----
  const listRef = useRef<HTMLDivElement>(null);
  const [drag, setDrag] = useState<Drag | null>(null);
  const live = useRef<{ pid: number; from: number; to: number; startY: number; lastY: number; scroller: HTMLElement; startScroll: number; raf: number } | null>(null);

  const rows = () => [...(listRef.current?.querySelectorAll<HTMLElement>("[data-slot]") ?? [])];
  const scrollerOf = (el: HTMLElement): HTMLElement => {
    for (let n = el.parentElement; n; n = n.parentElement) {
      const o = getComputedStyle(n).overflowY;
      if ((o === "auto" || o === "scroll") && n.scrollHeight > n.clientHeight) return n;
    }
    return (document.scrollingElement as HTMLElement) ?? document.documentElement;
  };
  const update = () => {
    const d = live.current;
    const box = listRef.current;
    if (!d || !box) return;
    const els = rows();
    const top = box.getBoundingClientRect().top;
    // where it would land: before the first row whose middle is below the pointer
    let k = els.length;
    for (let i = 0; i < els.length; i++) {
      if (i === d.from) continue;
      const r = els[i].getBoundingClientRect();
      if (d.lastY < r.top + r.height / 2) {
        k = i;
        break;
      }
    }
    const to = k > d.from ? k - 1 : k;
    d.to = to;
    const ref = els[Math.min(k, els.length - 1)].getBoundingClientRect();
    const line = to === d.from ? null : (k < els.length ? ref.top : ref.bottom) - top;
    setDrag({ pid: d.pid, from: d.from, to, dy: d.lastY - d.startY + (d.scroller.scrollTop - d.startScroll), line });
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
  const onGripDown = (i: number, pid: number) => (e: ReactPointerEvent<HTMLButtonElement>) => {
    if (e.button !== 0) return;
    e.preventDefault();
    e.currentTarget.setPointerCapture(e.pointerId);
    const scroller = scrollerOf(e.currentTarget);
    live.current = { pid, from: i, to: i, startY: e.clientY, lastY: e.clientY, scroller, startScroll: scroller.scrollTop, raf: 0 };
    document.body.classList.add("dragging-row");
    setDrag({ pid, from: i, to: i, dy: 0, line: null });
    live.current.raf = requestAnimationFrame(tick);
  };
  const onGripMove = (e: ReactPointerEvent) => {
    if (!live.current) return;
    live.current.lastY = e.clientY;
    update();
  };
  const finish = (commit: boolean) => {
    const d = live.current;
    if (!d) return;
    cancelAnimationFrame(d.raf);
    live.current = null;
    document.body.classList.remove("dragging-row");
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

  const row = (p: Player, i: number) => {
    const m = minutes[p.id] ?? 0;
    const s = seasonStatsOf(p, L.season, t.id);
    const dragging = drag?.pid === p.id;
    const role = i < 5 ? "Starter" : m > 0 ? (i === 5 ? "6th man" : "Bench") : "Out of rotation";
    return (
      <div key={p.id} data-slot={i} className={`rot-row${i < 5 ? " starter" : ""}${m === 0 ? " dnp" : ""}${dragging ? " dragging" : ""}`} style={dragging ? { transform: `translateY(${drag.dy}px)` } : undefined}>
        <button type="button" className="rot-grip" data-grip={p.id} onPointerDown={onGripDown(i, p.id)} onPointerMove={onGripMove} onPointerUp={() => finish(true)} onPointerCancel={() => finish(false)} onKeyDown={onGripKey(i)} aria-label={`Move ${p.first} ${p.last}: drag, or use the arrow keys`} title="Drag to move">
          <Grip />
        </button>
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
          sub={rot.auto ? "Auto: your staff sets it from ratings and positions. Drag anyone or change minutes to take over." : "Drag the handle to move a player. Drop him at the bottom to sit him."}
          flush
          right={
            <div className="row">
              <span className={`badge ${total === 200 ? "good" : "bad"}`} title="A game has 200 player-minutes (5 players × 40)">
                {total} / 200 min
              </span>
              {!rot.auto && total !== 200 && (
                <button className="btn btn-sm" onClick={scaleTo200}>
                  Scale to 200
                </button>
              )}
            </div>
          }
        >
          <div className="rot-list" ref={listRef}>
            <div className="rot-sec">
              <b>Starting five</b>
              <span className="faint">{note.text}</span>
              {note.warn && <span className="badge warn">{note.warn}</span>}
            </div>
            {order.slice(0, 5).map((p, i) => row(p, i))}
            {order.length > 5 && (
              <div className="rot-sec">
                <b>Bench</b>
                <span className="faint">If a starter is hurt, the first one here at his position starts</span>
              </div>
            )}
            {order.slice(5).map((p, i) => row(p, i + 5))}
            {drag?.line != null && <div className="rot-drop" style={{ top: drag.line - 1.5 }} />}
          </div>
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
              <li>Drag a player by the handle (or focus it and use the arrow keys). Each spot keeps its minutes, so moving your sixth man into the top five hands him a starter's minutes.</li>
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
