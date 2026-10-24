import { mutate, useLeague } from "../store";
import { roster, team } from "../../engine/core";
import { classLabel } from "../../engine/ratings";
import { autoRotation } from "../../engine/sim/rotation";
import { availablePlayers } from "../../engine/play";
import { Card, Grade, PageHead, PlayerLink } from "../components/common";
import { StatusBadges } from "./Roster";

export function RotationPage() {
  const L = useLeague();
  const t = team(L, L.userTid);
  const all = roster(L, t.id);
  const avail = availablePlayers(L, t.id);
  const auto = autoRotation(avail);
  const rot = t.rotation;
  const starters = rot.auto ? auto.starters : rot.starters;
  const minutes = rot.auto ? auto.minutes : rot.minutes;
  const total = avail.reduce((a, p) => a + (minutes[p.id] ?? 0), 0);
  const ordered = all.slice().sort((a, b) => {
    const sa = starters.includes(a.id) ? 1 : 0;
    const sb = starters.includes(b.id) ? 1 : 0;
    if (sa !== sb) return sb - sa;
    return (minutes[b.id] ?? 0) - (minutes[a.id] ?? 0) || b.ovr - a.ovr;
  });
  const takeManual = () =>
    mutate(() => {
      t.rotation = { auto: false, starters: auto.starters.slice(), minutes: { ...auto.minutes } };
    });
  const toggleStarter = (pid: number) =>
    mutate(() => {
      if (t.rotation.auto) t.rotation = { auto: false, starters: auto.starters.slice(), minutes: { ...auto.minutes } };
      const s = t.rotation.starters;
      if (s.includes(pid)) t.rotation.starters = s.filter((x) => x !== pid);
      else if (s.length < 5) s.push(pid);
      else {
        s.pop();
        s.push(pid);
      }
    });
  const setMin = (pid: number, v: number) =>
    mutate(() => {
      if (t.rotation.auto) t.rotation = { auto: false, starters: auto.starters.slice(), minutes: { ...auto.minutes } };
      t.rotation.minutes[pid] = Math.max(0, Math.min(40, Math.round(v)));
    });
  const balance = () =>
    mutate(() => {
      const ids = avail.map((p) => p.id);
      let sum = ids.reduce((a, id) => a + (t.rotation.minutes[id] ?? 0), 0);
      if (sum <= 0) return;
      for (const id of ids) t.rotation.minutes[id] = Math.round(((t.rotation.minutes[id] ?? 0) * 200) / sum);
      sum = ids.reduce((a, id) => a + (t.rotation.minutes[id] ?? 0), 0);
      const top = ids.slice().sort((a, b) => (t.rotation.minutes[b] ?? 0) - (t.rotation.minutes[a] ?? 0))[0];
      t.rotation.minutes[top] += 200 - sum;
    });
  return (
    <div>
      <PageHead
        title="Rotation"
        sub="Pick your starting five and target minutes. In games, the coach subs toward these targets, around fatigue and foul trouble, and goes to the best five late in close games."
        right={
          <div className="row">
            <label className="check">
              <input
                type="checkbox"
                checked={rot.auto}
                onChange={(e) =>
                  e.target.checked ? mutate(() => void (t.rotation = { auto: true, starters: [], minutes: {} })) : takeManual()
                }
              />
              Auto rotation
            </label>
          </div>
        }
      />
      <div className="grid g-main">
        <Card
          title="Depth Chart"
          sub={rot.auto ? "Auto: starters and minutes follow ratings and positional balance." : "Manual rotation"}
          flush
          right={
            !rot.auto ? (
              <div className="row">
                <span className={`badge ${total === 200 ? "good" : "bad"}`}>{total} / 200 min</span>
                <button className="btn btn-sm" onClick={balance}>
                  Scale to 200
                </button>
              </div>
            ) : null
          }
        >
          <table className="tbl">
            <thead>
              <tr>
                <th style={{ width: 70 }}>Starter</th>
                <th>Player</th>
                <th>Pos</th>
                <th>Class</th>
                <th className="n">OVR</th>
                <th style={{ width: 260 }}>Minutes</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {ordered.map((p) => {
                const unavailable = !avail.includes(p);
                const m = minutes[p.id] ?? 0;
                return (
                  <tr key={p.id} className={unavailable ? "dim" : starters.includes(p.id) ? "hl" : ""}>
                    <td className="c">
                      <input type="checkbox" disabled={unavailable} checked={starters.includes(p.id)} onChange={() => toggleStarter(p.id)} style={{ width: 16, height: 16, accentColor: "var(--accent)" }} />
                    </td>
                    <td>
                      <PlayerLink L={L} p={p} face size={26} colors={t.colors} />
                    </td>
                    <td>{p.pos}</td>
                    <td>{classLabel(p)}</td>
                    <td className="n">
                      <Grade v={p.ovr} />
                    </td>
                    <td>
                      <div className="row">
                        <input type="range" min={0} max={40} value={unavailable ? 0 : m} disabled={unavailable} onChange={(e) => setMin(p.id, Number(e.target.value))} />
                        <span className="num bold" style={{ width: 22, textAlign: "right" }}>
                          {unavailable ? "-" : m}
                        </span>
                      </div>
                    </td>
                    <td>
                      <StatusBadges L={L} p={p} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Card>
        <div className="col gap-16">
          <Card title="How rotations work">
            <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.6 }}>
              <li>Starters open each half.</li>
              <li>Players tire on the floor and recover on the bench; tired players perform worse.</li>
              <li>Two first-half fouls or four second-half fouls send a player to the bench.</li>
              <li>Blowouts empty the bench; close games late go to your best five.</li>
              <li>Injured and redshirting players are skipped automatically.</li>
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
