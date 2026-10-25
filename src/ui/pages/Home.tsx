import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { deleteLeague, importLeague, listLeagues, type LeagueMeta, type SyncRec } from "../db";
import { heroStyle, Logo } from "../components/common";
import { Icon } from "../components/Icons";
import { PHASE_LABEL, seasonLabel } from "../../engine/core";
import { getLeague, setLeague } from "../store";
import { cloudOn, deleteCloudLeague, formatCode, getCode, listCloud, pullLeague, pushUnsynced, switchCode, syncRecords, useCloudStatus, type CloudLeague } from "../cloud";
import { cloudLine } from "../components/CloudCard";

interface Row {
  meta: LeagueMeta;
  local: boolean;
  cloud: CloudLeague | null;
  /** the cloud has newer progress than this device */
  newer: boolean;
}

const FEATURES: [string, string, string][] = [
  ["history", "Nothing gets deleted", "Every season, roster, box score, bracket and record stays browsable forever."],
  ["recruit", "Recruit like a coach", "Calls, visits, offers and NIL against AI programs playing by the same rules."],
  ["bracket", "Real March", "Conference tournaments, Selection Sunday, the First Four and upsets that feel earned."],
  ["crown", "Build a Blue Blood", "Take any of 365 programs from nowhere to the top. Or move up the coaching ladder."],
];

export function Home() {
  const [leagues, setLeagues] = useState<LeagueMeta[] | null>(null);
  const [cloud, setCloud] = useState<CloudLeague[] | null>(null);
  const [cloudErr, setCloudErr] = useState(false);
  const [recs, setRecs] = useState<Map<string, SyncRec>>(new Map());
  const [loading, setLoading] = useState<{ lid: string; done: number; total: number } | null>(null);
  const [importing, setImporting] = useState(false);
  const [codeInput, setCodeInput] = useState("");
  const [codeOpen, setCodeOpen] = useState(false);
  const st = useCloudStatus();
  const nav = useNavigate();
  const loc = useLocation();
  const fileRef = useRef<HTMLInputElement>(null);
  const refresh = async () => {
    void listLeagues().then(setLeagues);
    void syncRecords().then(setRecs);
    if (!cloudOn()) {
      setCloud([]);
      return;
    }
    try {
      setCloud(await listCloud());
      setCloudErr(false);
    } catch {
      setCloud([]);
      setCloudErr(true);
    }
  };
  useEffect(() => {
    document.title = "Hardwood Dynasty";
    void refresh();
    // leagues from before cloud saves existed go up now
    void pushUnsynced();
  }, []);
  // merge this device's leagues with the cloud's
  const rows: Row[] = [];
  if (leagues) {
    const byId = new Map((cloud ?? []).map((c) => [c.manifest.lid, c]));
    for (const m of leagues) {
      const c = byId.get(m.id) ?? null;
      const newer = !!c && c.manifest.updated > m.updated && recs.get(m.id)?.head !== c.manifest.head;
      rows.push({ meta: newer && c ? c.manifest.meta : m, local: true, cloud: c, newer });
      byId.delete(m.id);
    }
    for (const c of byId.values()) rows.push({ meta: c.manifest.meta, local: false, cloud: c, newer: true });
    rows.sort((a, b) => b.meta.updated - a.meta.updated);
  }
  const open = async (r: Row) => {
    if (r.newer && r.cloud) {
      setLoading({ lid: r.meta.id, done: 0, total: 1 });
      try {
        await pullLeague(r.cloud, (done, total) => setLoading({ lid: r.meta.id, done, total }));
        if (getLeague()?.id === r.meta.id) setLeague(null);
      } catch (e) {
        setLoading(null);
        if (r.local && confirm(`Couldn't load the newer cloud save (${(e as Error).message}). Open the copy on this device instead?`)) nav(`/l/${r.meta.id}`);
        else if (!r.local) alert(`Couldn't load this league from the cloud: ${(e as Error).message}`);
        return;
      }
      setLoading(null);
    }
    nav(`/l/${r.meta.id}`);
  };
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
        <div className={`home-cloud ${st.state}`}>
          <Icon name="cloud" size={16} />
          <span>
            {cloudOn() ? (
              <>
                <b>Cloud saves {cloudErr ? "unreachable right now" : "on"}.</b> {loc.search.includes("linked=1") ? "Linked to your other device's code." : cloudErr ? "Your leagues are still saved on this device." : cloudLine(st)}
              </>
            ) : (
              <>
                <b>Cloud saves off.</b> Turn them on in a league's Settings.
              </>
            )}
          </span>
          {cloudOn() && (
            <button className="home-link" onClick={() => setCodeOpen(!codeOpen)}>
              {codeOpen ? "Close" : "Use a code from another device"}
            </button>
          )}
        </div>
        {codeOpen && (
          <div className="home-codebox">
            <div style={{ color: "#a9b4c6", fontSize: 13 }}>
              Enter the save code from Settings on your other device. This device's code is <b style={{ color: "#fff" }}>{formatCode(getCode() ?? "")}</b>.
            </div>
            <div className="row" style={{ gap: 8, marginTop: 8 }}>
              <input className="input" style={{ maxWidth: 260, textTransform: "uppercase" }} placeholder="XXXX-XXXX-XXXX-XXXX" value={codeInput} onChange={(e) => setCodeInput(e.target.value)} />
              <button
                className="btn btn-white"
                disabled={!codeInput.trim()}
                onClick={async () => {
                  if (await switchCode(codeInput)) {
                    setCodeInput("");
                    setCodeOpen(false);
                    setCloud(null);
                    void refresh();
                  } else alert("That code doesn't look right. It has 16 letters and numbers.");
                }}
              >
                Load my leagues
              </button>
            </div>
          </div>
        )}
        {leagues === null || (cloud === null && leagues.length === 0) ? (
          <div style={{ color: "#8d99ae" }}>Loading…</div>
        ) : rows.length === 0 ? (
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
            {rows.map((r) => {
              const m = r.meta;
              const busy = loading?.lid === m.id;
              return (
              <div key={m.id} className="home-card" style={{ display: "flex", flexDirection: "column" }}>
                <a
                  href={`#/l/${m.id}`}
                  onClick={(e) => {
                    e.preventDefault();
                    void open(r);
                  }}
                  className="league-card-top hero-banner"
                  style={{ ...heroStyle(m.colors), borderRadius: 0, boxShadow: "none", border: "none" }}
                >
                  <Logo team={{ abbrev: m.teamAbbrev, colors: m.colors }} size={58} />
                  <div style={{ minWidth: 0, position: "relative" }}>
                    <div className="np-opp ellipsis">{m.teamName}</div>
                    <div className="small" style={{ opacity: 0.85 }}>
                      Coach {m.coach}
                    </div>
                  </div>
                  {r.cloud && (
                    <span className="league-cloud" title={r.newer ? (r.local ? "Newer progress from another device" : "Saved in the cloud") : "Saved in the cloud"}>
                      <Icon name="cloud" size={13} /> {r.newer ? (r.local ? "Newer save" : "In the cloud") : "Synced"}
                    </span>
                  )}
                </a>
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
                    <button className="btn btn-white" disabled={!!loading} onClick={() => void open(r)}>
                      {busy ? `Loading ${loading!.total > 1 ? `${Math.round((100 * loading!.done) / loading!.total)}%` : "…"}` : r.newer && !r.local ? "Load" : "Continue"}
                    </button>
                    <button
                      className="btn btn-sm btn-ghost"
                      style={{ color: "#ff8a8a", height: 22 }}
                      onClick={async () => {
                        if (!confirm(`Delete "${m.name}" (${m.teamName})${r.cloud ? " here and in the cloud" : ""}? This removes all of its history and cannot be undone.`)) return;
                        if (r.local) await deleteLeague(m.id);
                        if (r.cloud) await deleteCloudLeague(m.id).catch(() => alert("Couldn't remove the cloud copy right now."));
                        if (getLeague()?.id === m.id) setLeague(null);
                        void refresh();
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
              );
            })}
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
        <div style={{ color: "#5d6a80", fontSize: 12, marginTop: 44 }}>Leagues save in this browser and, with cloud saves on, to your save code so they follow you to other devices. Settings → Export league also downloads a backup file.</div>
      </div>
    </div>
  );
}
