import { mutate, useLeague } from "../store";
import { roster, team } from "../../engine/core";
import { classLabel, heightStr } from "../../engine/ratings";
import type { DefScheme, OffFocus, RebFocus, Strategy, Tempo, Tendencies } from "../../engine/types";
import { Card, Grade, PageHead, PlayerLink } from "../components/common";

const TEMPO: { k: Tempo; label: string; desc: string }[] = [
  { k: 1, label: "Grind", desc: "~62 possessions. Shorten the game; good for underdogs." },
  { k: 2, label: "Slow", desc: "~66 possessions. Patient half-court offense." },
  { k: 3, label: "Normal", desc: "~70 possessions. D1 average pace." },
  { k: 4, label: "Fast", desc: "~74 possessions. Push in transition." },
  { k: 5, label: "Run & Gun", desc: "~78 possessions. Maximum chaos; tires players out." },
];
const OFF: { k: OffFocus; label: string; desc: string }[] = [
  { k: "inside", label: "Inside", desc: "Feed the post and attack the rim. Fewer threes, more free throws." },
  { k: "balanced", label: "Balanced", desc: "Take what the defense gives." },
  { k: "perimeter", label: "Perimeter", desc: "Spread the floor and live by the three." },
];
const DEF: { k: DefScheme; label: string; desc: string }[] = [
  { k: "man", label: "Man-to-Man", desc: "Individual matchups decide it. Solid all-around." },
  { k: "zone", label: "2-3 Zone", desc: "Protects the paint and limits fouls, but concedes threes and offensive boards." },
  { k: "press", label: "Full-Court Press", desc: "Forces turnovers and speeds the game up, but gives up easy looks when broken and drains stamina." },
];
const REB: { k: RebFocus; label: string; desc: string }[] = [
  { k: "crash", label: "Crash the Glass", desc: "More offensive rebounds, weaker transition defense." },
  { k: "balanced", label: "Balanced", desc: "Standard rebounding responsibilities." },
  { k: "getback", label: "Get Back", desc: "Sacrifice offensive boards to stop fast breaks." },
];

function Choice<T extends string | number>({ title, opts, value, onChange }: { title: string; opts: { k: T; label: string; desc: string }[]; value: T; onChange: (k: T) => void }) {
  const cur = opts.find((o) => o.k === value);
  return (
    <div className="col gap-8">
      <div className="bold">{title}</div>
      <div className="btn-group">
        {opts.map((o) => (
          <button key={String(o.k)} className={`btn btn-sm ${o.k === value ? "on" : ""}`} onClick={() => onChange(o.k)}>
            {o.label}
          </button>
        ))}
      </div>
      <div className="small muted" style={{ minHeight: 36 }}>
        {cur?.desc}
      </div>
    </div>
  );
}

export function Tactics() {
  const L = useLeague();
  const t = team(L, L.userTid);
  const ps = roster(L, t.id).slice().sort((a, b) => b.ovr - a.ovr);
  const setS = <K extends keyof Strategy>(k: K, v: Strategy[K]) => mutate(() => void (t.strategy[k] = v));
  const setT = (pid: number, k: keyof Tendencies, v: number) =>
    mutate(() => {
      const p = ps.find((x) => x.id === pid);
      if (p) p.tend[k] = v;
    });
  return (
    <div>
      <PageHead title="Tactics" sub="Team strategy and player instructions apply to every game until you change them." />
      <Card title="Team Strategy">
        <div className="grid g2" style={{ gap: 24 }}>
          <Choice title="Tempo" opts={TEMPO} value={t.strategy.tempo} onChange={(v) => setS("tempo", v)} />
          <Choice title="Offensive Focus" opts={OFF} value={t.strategy.offense} onChange={(v) => setS("offense", v)} />
          <Choice title="Defense" opts={DEF} value={t.strategy.defense} onChange={(v) => setS("defense", v)} />
          <Choice title="Rebounding" opts={REB} value={t.strategy.rebounding} onChange={(v) => setS("rebounding", v)} />
        </div>
      </Card>
      <Card
        title="Player Instructions"
        sub="How often each player looks for each type of shot (5 = his natural tendency). Shot quality still depends on ratings and the defense."
        className="mt-16"
        flush
        right={
          <button className="btn btn-sm" onClick={() => mutate(() => ps.forEach((p) => (p.tend = { three: 5, mid: 5, inside: 5, drive: 5 })))}>
            Reset all to 5
          </button>
        }
      >
        <div className="tbl-wrap">
          <table className="tbl">
            <thead>
              <tr>
                <th>Player</th>
                <th>Pos</th>
                <th>Class</th>
                <th>Ht</th>
                <th className="n">OVR</th>
                <th className="n">3PT</th>
                <th className="n">MID</th>
                <th className="n">INS</th>
                <th style={{ width: 150 }}>Shoot 3</th>
                <th style={{ width: 150 }}>Shoot Mid-Range</th>
                <th style={{ width: 150 }}>Shoot Inside</th>
                <th style={{ width: 150 }}>Drive</th>
              </tr>
            </thead>
            <tbody>
              {ps.map((p) => (
                <tr key={p.id} className={p.redshirt ? "dim" : ""}>
                  <td>
                    <PlayerLink L={L} p={p} face size={26} colors={t.colors} />
                  </td>
                  <td>{p.pos}</td>
                  <td>{classLabel(p)}</td>
                  <td>{heightStr(p.hgt)}</td>
                  <td className="n">
                    <Grade v={p.ovr} />
                  </td>
                  <td className="n muted">{Math.round(p.r.three)}</td>
                  <td className="n muted">{Math.round(p.r.mid)}</td>
                  <td className="n muted">{Math.round(p.r.ins)}</td>
                  {(["three", "mid", "inside", "drive"] as (keyof Tendencies)[]).map((k) => (
                    <td key={k}>
                      <div className="row" style={{ gap: 6 }}>
                        <input type="range" min={0} max={10} value={p.tend[k]} onChange={(e) => setT(p.id, k, Number(e.target.value))} />
                        <span className="num bold" style={{ width: 16, color: p.tend[k] === 5 ? "var(--muted)" : "var(--text)" }}>
                          {p.tend[k]}
                        </span>
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
