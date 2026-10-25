import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { deleteLeague, importLeague, listLeagues, type LeagueMeta } from "../db";
import { heroStyle, Logo } from "../components/common";
import { Icon } from "../components/Icons";
import { PHASE_LABEL, seasonLabel } from "../../engine/core";
import { getLeague, setLeague } from "../store";

const FEATURES: [string, string, string][] = [
  ["history", "Nothing gets deleted", "Every season, roster, box score, bracket and record stays browsable forever."],
  ["recruit", "Recruit like a coach", "Calls, visits, offers and NIL against AI programs playing by the same rules."],
  ["bracket", "Real March", "Conference tournaments, Selection Sunday, the First Four and upsets that feel earned."],
  ["crown", "Build a Blue Blood", "Take any of 365 programs from nowhere to the top. Or move up the coaching ladder."],
];

export function Home() {
  const [leagues, setLeagues] = useState<LeagueMeta[] | null>(null);
  const [importing, setImporting] = useState(false);
  const nav = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const refresh = () => listLeagues().then(setLeagues);
  useEffect(() => {
    document.title = "Hardwood Dynasty";
    refresh();
  }, []);
  return (
    <div className="home-wrap">
      <div className="home-inner">
        <div className="row" style={{ gap: 12, marginBottom: 26 }}>
          <span className="brand-mark" style={{ width: 40, height: 40, borderRadius: 11 }}>
            <Icon name="crown" size={23} />
          </span>
          <span className="brand-name" style={{ fontSize: 20, color: "#fff" }}>
            Hardwood Dynasty
          </span>
        </div>
        <div className="home-title">
          Build a <span>dynasty.</span>
        </div>
        <p style={{ color: "#a9b4c6", fontSize: 17, maxWidth: 620, margin: "16px 0 26px", lineHeight: 1.5 }}>
          A college basketball program builder. Pick any school, recruit, develop, survive March, and watch your program's history grow season after season.
        </p>
        <div className="row" style={{ gap: 10 }}>
          <Link to="/new" className="cta">
            <Icon name="plus" size={17} /> New League
          </Link>
          <button className="ghost-light" disabled={importing} onClick={() => fileRef.current?.click()}>
            <Icon name="upload" size={16} /> {importing ? "Importing…" : "Import Save"}
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".hdsave,.gz,.json,application/gzip,application/json"
            style={{ display: "none" }}
            onChange={async (e) => {
              const f = e.target.files?.[0];
              if (!f) return;
              setImporting(true);
              try {
                const id = await importLeague(f);
                await refresh();
                nav(`/l/${id}`);
              } catch (err) {
                alert(`Import failed: ${(err as Error).message}`);
              }
              setImporting(false);
              e.target.value = "";
            }}
          />
        </div>

        <div className="section-title" style={{ marginTop: 52, color: "#8d99ae" }}>
          Your leagues
        </div>
        {leagues === null ? (
          <div style={{ color: "#8d99ae" }}>Loading…</div>
        ) : leagues.length === 0 ? (
          <div className="home-card home-empty" style={{ padding: 30, display: "flex", alignItems: "center", gap: 22 }}>
            <span className="feature">
              <span className="fi" style={{ width: 52, height: 52, borderRadius: 14 }}>
                <Icon name="ball" size={26} />
              </span>
            </span>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: "#fff" }}>No leagues yet</div>
              <div style={{ color: "#8d99ae", marginTop: 4 }}>Start a new league, pick a program, and take the job.</div>
            </div>
            <Link to="/new" className="cta">
              Start your first league
            </Link>
          </div>
        ) : (
          <div className="grid g3">
            {leagues.map((m) => (
              <div key={m.id} className="home-card" style={{ display: "flex", flexDirection: "column" }}>
                <Link to={`/l/${m.id}`} className="league-card-top hero-banner" style={{ ...heroStyle(m.colors), borderRadius: 0, boxShadow: "none", border: "none" }}>
                  <Logo team={{ abbrev: m.teamAbbrev, colors: m.colors }} size={58} />
                  <div style={{ minWidth: 0, position: "relative" }}>
                    <div className="np-opp ellipsis">{m.teamName}</div>
                    <div className="small" style={{ opacity: 0.85 }}>
                      Coach {m.coach}
                    </div>
                  </div>
                </Link>
                <div className="league-card-body">
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ color: "#fff", fontWeight: 650 }} className="ellipsis">
                      {m.name}
                    </div>
                    <div style={{ color: "#8d99ae", fontSize: 12.5 }} className="ellipsis">
                      {seasonLabel(m.season)} · {PHASE_LABEL[m.phase as keyof typeof PHASE_LABEL] ?? m.phase} · <b style={{ color: "#c3ccda" }}>{m.record}</b>
                    </div>
                    <div style={{ color: "#5d6a80", fontSize: 11.5, marginTop: 2 }}>Last played {new Date(m.updated).toLocaleDateString()}</div>
                  </div>
                  <div className="col" style={{ gap: 4, alignItems: "flex-end" }}>
                    <Link to={`/l/${m.id}`} className="btn btn-white">
                      Continue
                    </Link>
                    <button
                      className="btn btn-sm btn-ghost"
                      style={{ color: "#ff8a8a", height: 22 }}
                      onClick={async () => {
                        if (!confirm(`Delete "${m.name}" (${m.teamName})? This removes all of its history and cannot be undone.`)) return;
                        await deleteLeague(m.id);
                        if (getLeague()?.id === m.id) setLeague(null);
                        refresh();
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="grid g4" style={{ marginTop: 52, gap: 22 }}>
          {FEATURES.map(([icon, title, text]) => (
            <div key={title} className="feature">
              <span className="fi">
                <Icon name={icon} />
              </span>
              <div>
                <b>{title}</b>
                <span>{text}</span>
              </div>
            </div>
          ))}
        </div>
        <div style={{ color: "#5d6a80", fontSize: 12, marginTop: 44 }}>Saves live in this browser. Use Settings → Export league to back up a league to a file.</div>
      </div>
    </div>
  );
}
