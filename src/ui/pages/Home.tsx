import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { deleteLeague, importLeague, listLeagues, type LeagueMeta } from "../db";
import { Logo } from "../components/common";
import { Icon } from "../components/Icons";
import { PHASE_LABEL, seasonLabel } from "../../engine/core";
import { getLeague, setLeague } from "../store";

export function Home() {
  const [leagues, setLeagues] = useState<LeagueMeta[] | null>(null);
  const nav = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const refresh = () => listLeagues().then(setLeagues);
  useEffect(() => {
    document.title = "Hardwood Dynasty";
    document.documentElement.style.removeProperty("--accent");
    refresh();
  }, []);
  return (
    <div className="home-wrap">
      <div className="home-inner">
        <div className="row" style={{ gap: 14, marginBottom: 6 }}>
          <div style={{ width: 56, height: 56, borderRadius: 14, background: "#93c5fd", color: "#111827", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Icon name="crown" size={34} />
          </div>
          <div>
            <div className="home-title">Hardwood Dynasty</div>
            <div style={{ color: "#9fb0c8", fontSize: 15 }}>College basketball program builder. Take any program from nowhere to Blue Blood.</div>
          </div>
        </div>
        <div className="row mt-24 mb-16">
          <h2 style={{ color: "#fff" }}>Your Leagues</h2>
          <div className="spacer" />
          <button className="btn" onClick={() => fileRef.current?.click()}>
            Import Save
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".json,.gz,application/json,application/gzip"
            style={{ display: "none" }}
            onChange={async (e) => {
              const f = e.target.files?.[0];
              if (!f) return;
              try {
                const id = await importLeague(f);
                await refresh();
                nav(`/l/${id}`);
              } catch (err) {
                alert(`Import failed: ${(err as Error).message}`);
              }
              e.target.value = "";
            }}
          />
          <Link to="/new" className="btn btn-lg" style={{ background: "#93c5fd", color: "#0b1020", border: "none", fontWeight: 750 }}>
            + New League
          </Link>
        </div>
        {leagues === null ? (
          <div style={{ color: "#9fb0c8" }}>Loading…</div>
        ) : leagues.length === 0 ? (
          <div className="home-card" style={{ padding: 32, textAlign: "center" }}>
            <div style={{ fontSize: 18, fontWeight: 650, color: "#fff" }}>No leagues yet</div>
            <div style={{ color: "#9fb0c8", marginTop: 6 }}>Start a new league, pick a program, and build a dynasty. Every season, player, box score and record is kept forever.</div>
            <Link to="/new" className="btn btn-lg mt-16" style={{ background: "#93c5fd", color: "#0b1020", border: "none", fontWeight: 750 }}>
              Start your first league
            </Link>
          </div>
        ) : (
          <div className="grid g2">
            {leagues.map((m) => (
              <div key={m.id} className="home-card row" style={{ gap: 14 }}>
                <Logo team={{ abbrev: m.teamAbbrev, colors: m.colors }} size={52} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 16, fontWeight: 700, color: "#fff" }}>{m.teamName}</div>
                  <div style={{ color: "#9fb0c8", fontSize: 12.5 }}>
                    {m.name} · Coach {m.coach}
                  </div>
                  <div style={{ color: "#c8d3e3", fontSize: 12.5, marginTop: 2 }}>
                    {seasonLabel(m.season)} · {PHASE_LABEL[m.phase as keyof typeof PHASE_LABEL] ?? m.phase} · {m.record}
                  </div>
                  <div style={{ color: "#7f8ea6", fontSize: 11.5 }}>Last played {new Date(m.updated).toLocaleString()}</div>
                </div>
                <div className="col">
                  <Link to={`/l/${m.id}`} className="btn" style={{ background: "#fff", color: "#111827", border: "none", fontWeight: 700 }}>
                    Continue
                  </Link>
                  <button
                    className="btn btn-sm btn-ghost"
                    style={{ color: "#fca5a5" }}
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
            ))}
          </div>
        )}
        <div style={{ color: "#6f7f98", fontSize: 12, marginTop: 40 }}>
          Saves live in this browser (IndexedDB). Use Settings → Export to back up a league to a file.
        </div>
      </div>
    </div>
  );
}
