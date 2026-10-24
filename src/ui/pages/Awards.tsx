import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { seasonLabel, team } from "../../engine/core";
import type { AwardEntry, League } from "../../engine/types";
import { Card, Empty, Logo, PageHead } from "../components/common";

function Entry({ L, a, big }: { L: League; a: AwardEntry; big?: boolean }) {
  const t = team(L, a.tid);
  return (
    <div className="row" style={{ gap: 12, padding: big ? "10px 0" : "6px 0", borderBottom: "1px solid var(--border)" }}>
      <Logo team={t} size={big ? 40 : 30} />
      <div style={{ flex: 1 }}>
        {a.pid !== undefined ? (
          <Link to={`/l/${L.id}/player/${a.pid}`} className="bold" style={{ fontSize: big ? 16 : 13.5 }}>
            {a.playerName}
          </Link>
        ) : (
          <span className="bold" style={{ fontSize: big ? 16 : 13.5 }}>
            {a.playerName}
          </span>
        )}
        <div className="small muted">
          <Link to={`/l/${L.id}/team/${t.id}`}>{t.name}</Link> · {a.line}
        </div>
      </div>
    </div>
  );
}

export function Awards() {
  const L = useLeague();
  const seasons = L.awards.map((a) => a.season).reverse();
  const [season, setSeason] = useState<number>(seasons[0] ?? L.season);
  const [conf, setConf] = useState<number>(team(L, L.userTid).cid);
  const aw = L.awards.find((a) => a.season === season);
  if (!aw)
    return (
      <div>
        <PageHead title="Awards" />
        <Card>
          <Empty>Awards are handed out after the national championship game.</Empty>
        </Card>
      </div>
    );
  const ca = aw.conf[conf];
  return (
    <div>
      <PageHead
        title="Awards"
        sub={seasonLabel(season)}
        right={
          <select className="select" value={season} onChange={(e) => setSeason(Number(e.target.value))}>
            {seasons.map((s) => (
              <option key={s} value={s}>
                {seasonLabel(s)}
              </option>
            ))}
          </select>
        }
      />
      <div className="grid g-main">
        <div className="col gap-16">
          <Card title="National Awards">
            {aw.national.map((a) => (
              <div key={a.name}>
                <div className="tiny muted bold mt-8" style={{ textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  {a.name}
                </div>
                <Entry L={L} a={a} big={a.name === "Player of the Year"} />
              </div>
            ))}
          </Card>
          {aw.allAmerica.map((teamList, i) => (
            <Card key={i} title={["First Team All-America", "Second Team All-America", "Third Team All-America"][i]}>
              {teamList.map((a) => (
                <Entry key={a.pid} L={L} a={a} />
              ))}
            </Card>
          ))}
        </div>
        <div className="col gap-16">
          <Card
            title="Conference Awards"
            right={
              <select className="select" value={conf} onChange={(e) => setConf(Number(e.target.value))}>
                {L.conferences.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.short}
                  </option>
                ))}
              </select>
            }
          >
            {ca ? (
              <>
                {ca.awards.map((a) => (
                  <div key={a.name}>
                    <div className="tiny muted bold mt-8" style={{ textTransform: "uppercase" }}>
                      {a.name}
                    </div>
                    <Entry L={L} a={a} />
                  </div>
                ))}
                {ca.teams.map((tl, i) => (
                  <div key={i}>
                    <div className="tiny muted bold mt-16" style={{ textTransform: "uppercase" }}>
                      {i === 0 ? "First Team" : "Second Team"}
                    </div>
                    {tl.map((a) => (
                      <Entry key={a.pid} L={L} a={a} />
                    ))}
                  </div>
                ))}
              </>
            ) : (
              <div className="muted">No awards.</div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
