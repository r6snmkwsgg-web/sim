import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { deleteLeague, importLeague, listLeagues, type LeagueMeta, type SyncRec } from "../db";
import { Logo } from "../components/common";
import { Floor } from "../components/Floor";
import { Icon } from "../components/Icons";
import { PHASE_LABEL, seasonLabel } from "../../engine/core";
import { getLeague, setLeague } from "../store";
import { cloudOn, deleteCloudLeague, formatCode, getCode, listCloud, pullLeague, pushUnsynced, switchCode, syncRecords, useCloudStatus, type CloudLeague } from "../cloud";
import { cloudLine } from "../components/CloudCard";
import teamData from "../../engine/data/teams.json";
import confData from "../../engine/data/conferences.json";

interface Row {
  meta: LeagueMeta;
  local: boolean;
  cloud: CloudLeague | null;
  /** the cloud has newer progress than this device */
  newer: boolean;
}

const TEAM_COUNT = teamData.length;
const FACTS: [string, string][] = [
  ["Programs", `${TEAM_COUNT}, in ${confData.length} conferences`],
  ["Recruits a class", "1,500 to 1,900"],
  ["March", "68 teams, First Four to the title game"],
  ["Transfer portal", "Four windows every spring"],
  ["NIL", "Budgets set by each school's boosters"],
  ["Kept forever", "Every box score"],
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
  const importer = (
    <>
      <button className="land-text-btn" disabled={importing} onClick={() => fileRef.current?.click()}>
        {importing ? "Importing…" : "Import a save file"}
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
    </>
  );
  const about = (
    <section className="land-about">
      <div>
        <p className="land-lede">
          You're the new head coach. Take over any of the {TEAM_COUNT} Division I programs, recruit high schoolers and transfers, coach the games, and find out how long you can keep the job.
        </p>
        <p className="land-sub">Nothing gets thrown away: every box score, bracket and signing class stays in the record book.</p>
        <div className="land-actions">
          <Link to="/new" className="land-btn">
            Start a new league
          </Link>
          {importer}
        </div>
      </div>
      <dl className="land-facts">
        <div className="land-facts-h">Quick facts</div>
        {FACTS.map(([k, v]) => (
          <div key={k}>
            <dt>{k}</dt>
            <dd>{v}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
  const loaded = !(leagues === null || (cloud === null && leagues.length === 0));
  return (
    <div className="home-wrap land">
      <Floor title="Hardwood Dynasty" />
      <main className="land-inner">
        {loaded && rows.length === 0 && about}
        <section>
          <div className="land-head">
            <h2>Your leagues</h2>
            {rows.length > 0 && (
              <Link to="/new" className="land-btn small">
                New league
              </Link>
            )}
          </div>
          <div className={`land-cloud ${st.state}`}>
            <Icon name="cloud" size={15} />
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
              <button className="land-text-btn" onClick={() => setCodeOpen(!codeOpen)}>
                {codeOpen ? "Close" : "Use a code from another device"}
              </button>
            )}
          </div>
          {codeOpen && (
            <div className="land-codebox">
              <div>
                Enter the save code from Settings on your other device. This device's code is <b>{formatCode(getCode() ?? "")}</b>.
              </div>
              <div className="row" style={{ gap: 8, marginTop: 8, flexWrap: "wrap" }}>
                <input className="input" style={{ maxWidth: 260, textTransform: "uppercase" }} placeholder="XXXX-XXXX-XXXX-XXXX" value={codeInput} onChange={(e) => setCodeInput(e.target.value)} />
                <button
                  className="land-btn small"
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
          {!loaded ? (
            <div className="land-muted">Loading…</div>
          ) : rows.length === 0 ? (
            <div className="land-muted">Nothing saved on this device yet.</div>
          ) : (
            <div className="land-list">
              {rows.map((r) => {
                const m = r.meta;
                const busy = loading?.lid === m.id;
                return (
                  <div key={m.id} className="land-row" style={{ ["--team" as string]: m.colors[0] }}>
                    <a
                      href={`#/l/${m.id}`}
                      className="land-row-team"
                      onClick={(e) => {
                        e.preventDefault();
                        void open(r);
                      }}
                    >
                      <Logo team={{ abbrev: m.teamAbbrev, colors: m.colors }} size={44} />
                      <span style={{ minWidth: 0 }}>
                        <span className="land-row-name ellipsis">{m.teamName}</span>
                        <span className="land-row-sub ellipsis">
                          Coach {m.coach} · {m.name}
                        </span>
                      </span>
                    </a>
                    <div className="land-row-season">
                      <span>{seasonLabel(m.season)}</span>
                      <span className="land-muted">{PHASE_LABEL[m.phase as keyof typeof PHASE_LABEL] ?? m.phase}</span>
                    </div>
                    <div className="land-row-rec">{m.record}</div>
                    <div className="land-row-when land-muted">
                      {r.cloud ? (r.newer ? (r.local ? "Newer save in the cloud" : "In the cloud") : "Synced") : "This device"}
                      <br />
                      Played {new Date(m.updated).toLocaleDateString()}
                    </div>
                    <div className="land-row-act">
                      <button className="land-btn small" disabled={!!loading} onClick={() => void open(r)}>
                        {busy ? `Loading ${loading!.total > 1 ? `${Math.round((100 * loading!.done) / loading!.total)}%` : "…"}` : r.newer && !r.local ? "Load" : "Continue"}
                      </button>
                      <button
                        className="land-text-btn danger"
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
                );
              })}
            </div>
          )}
        </section>
        {loaded && rows.length > 0 && about}
        <footer className="land-foot">Leagues save in this browser and, with cloud saves on, to your save code so they follow you to other devices. Settings, then Export league, downloads a backup file.</footer>
      </main>
    </div>
  );
}
