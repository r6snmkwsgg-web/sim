import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createLeague, DEFAULT_SETTINGS, teamCatalog } from "../../engine/league";
import type { Settings } from "../../engine/types";
import { prestigeTier, prestigeStars } from "../../engine/ratings";
import { Logo, Stars } from "../components/common";
import { reindex } from "../../engine/core";
import { save, setLeague } from "../store";

const FIRST = ["Mike", "Tom", "Bill", "Roy", "Rick", "Scott", "Jay", "Kelvin", "Dana", "Shaka", "Nate", "Bruce", "Tony", "Danny", "Greg"];
const LAST = ["Walker", "Bennett", "Hayes", "Painter", "Calhoun", "Drew", "Few", "Self", "Odom", "Pearl", "Sampson", "Wright", "Bennett", "Turner", "Brooks"];

export function NewLeague() {
  const cat = useMemo(() => teamCatalog(), []);
  const nav = useNavigate();
  const [conf, setConf] = useState<string>("all");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<"prestige" | "name">("prestige");
  const [slug, setSlug] = useState<string>(() => cat.teams.filter((t) => t.prestige < 35)[Math.floor(Math.random() * 60)]?.slug ?? cat.teams[0].slug);
  const [first, setFirst] = useState(FIRST[Math.floor(Math.random() * FIRST.length)]);
  const [last, setLast] = useState(LAST[Math.floor(Math.random() * LAST.length)]);
  const [name, setName] = useState("My Dynasty");
  const [settings, setSettings] = useState<Settings>({ ...DEFAULT_SETTINGS });
  const [creating, setCreating] = useState(false);
  const selected = cat.teams.find((t) => t.slug === slug)!;
  const confName = (s: string) => cat.conferences.find((c) => c.slug === s)?.short ?? s;
  const list = cat.teams
    .filter((t) => (conf === "all" || t.conf === conf) && (!q || `${t.name} ${t.mascot}`.toLowerCase().includes(q.toLowerCase())))
    .sort((a, b) => (sort === "prestige" ? b.prestige - a.prestige : a.name.localeCompare(b.name)));
  const set = <K extends keyof Settings>(k: K, v: Settings[K]) => setSettings((s) => ({ ...s, [k]: v }));
  const create = async () => {
    setCreating(true);
    await new Promise((r) => setTimeout(r, 30));
    try {
      const L = createLeague({ name: name.trim() || "My Dynasty", teamSlug: slug, coachFirst: first.trim(), coachLast: last.trim(), settings });
      reindex(L);
      setLeague(L);
      await save();
      nav(`/l/${L.id}`);
    } catch (e) {
      console.error(e);
      alert(`Could not create league: ${(e as Error).message}`);
      setCreating(false);
    }
  };
  const pick = (filter: (t: (typeof cat.teams)[number]) => boolean) => {
    const c = cat.teams.filter(filter);
    setSlug(c[Math.floor(Math.random() * c.length)].slug);
  };
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "28px 24px" }}>
        <div className="row mb-16">
          <Link to="/" className="btn btn-ghost">
            ‹ Back
          </Link>
          <h1>New League</h1>
        </div>
        <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1.5fr) minmax(0, 1fr)" }}>
          <div className="card">
            <div className="card-h">
              <h2>Choose your program</h2>
              <div className="spacer" />
              <button className="btn btn-sm" onClick={() => pick((t) => t.prestige < 30)}>
                Random low-major
              </button>
              <button className="btn btn-sm" onClick={() => pick(() => true)}>
                Random program
              </button>
            </div>
            <div className="card-b row-wrap" style={{ borderBottom: "1px solid var(--border)" }}>
              <input className="input" placeholder="Search programs…" value={q} onChange={(e) => setQ(e.target.value)} style={{ width: 220 }} />
              <select className="select" value={conf} onChange={(e) => setConf(e.target.value)}>
                <option value="all">All conferences</option>
                {cat.conferences.map((c) => (
                  <option key={c.slug} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
              <select className="select" value={sort} onChange={(e) => setSort(e.target.value as "prestige" | "name")}>
                <option value="prestige">Sort by prestige</option>
                <option value="name">Sort by name</option>
              </select>
              <span className="muted small">{list.length} programs</span>
            </div>
            <div style={{ maxHeight: "62vh", overflowY: "auto" }}>
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Program</th>
                    <th>Conference</th>
                    <th>Prestige</th>
                    <th>Tier</th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((t) => (
                    <tr key={t.slug} className={`clickable ${t.slug === slug ? "hl" : ""}`} onClick={() => setSlug(t.slug)}>
                      <td>
                        <span className="team-cell">
                          <Logo team={t} size={24} />
                          <b>{t.name}</b> <span className="muted">{t.mascot}</span>
                        </span>
                      </td>
                      <td>{confName(t.conf)}</td>
                      <td>
                        <Stars n={prestigeStars(t.prestige)} />
                      </td>
                      <td className="muted">{prestigeTier(t.prestige)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="col gap-16">
            <div className="card" style={{ overflow: "hidden" }}>
              <div style={{ background: selected.colors[0], padding: 20, display: "flex", gap: 16, alignItems: "center" }}>
                <Logo team={selected} size={72} />
                <div style={{ color: luminance(selected.colors[0]) > 0.45 ? "#111" : "#fff" }}>
                  <div style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em" }}>{selected.name}</div>
                  <div style={{ opacity: 0.85 }}>
                    {selected.mascot} · {selected.city}, {selected.state}
                  </div>
                </div>
              </div>
              <div className="card-b">
                <dl className="kv">
                  <dt>Conference</dt>
                  <dd>{cat.conferences.find((c) => c.slug === selected.conf)?.name}</dd>
                  <dt>Prestige</dt>
                  <dd>
                    <Stars n={prestigeStars(selected.prestige)} /> <span className="muted">({prestigeTier(selected.prestige)})</span>
                  </dd>
                  <dt>Challenge</dt>
                  <dd>{selected.prestige >= 85 ? "Defend a dynasty" : selected.prestige >= 65 ? "Contender rebuild" : selected.prestige >= 45 ? "Mid-major climb" : "From no-name to Blue Blood"}</dd>
                </dl>
              </div>
            </div>
            <div className="card">
              <div className="card-h">
                <h2>Coach & League</h2>
              </div>
              <div className="card-b col gap-12">
                <div className="row">
                  <div className="field" style={{ flex: 1 }}>
                    <label>First name</label>
                    <input className="input" value={first} onChange={(e) => setFirst(e.target.value)} />
                  </div>
                  <div className="field" style={{ flex: 1 }}>
                    <label>Last name</label>
                    <input className="input" value={last} onChange={(e) => setLast(e.target.value)} />
                  </div>
                </div>
                <div className="field">
                  <label>League name</label>
                  <input className="input" value={name} onChange={(e) => setName(e.target.value)} />
                </div>
                <div className="divider" />
                <label className="check">
                  <input type="checkbox" checked={settings.portal} onChange={(e) => set("portal", e.target.checked)} /> Transfer portal
                </label>
                <label className="check">
                  <input type="checkbox" checked={settings.nil} onChange={(e) => set("nil", e.target.checked)} /> NIL deals in recruiting
                </label>
                <label className="check">
                  <input type="checkbox" checked={settings.canBeFired} onChange={(e) => set("canBeFired", e.target.checked)} /> You can be fired
                </label>
                <label className="check">
                  <input type="checkbox" checked={settings.injuries} onChange={(e) => set("injuries", e.target.checked)} /> Injuries
                </label>
                <div className="row">
                  <div className="field" style={{ flex: 1 }}>
                    <label>NCAA field</label>
                    <select className="select" value={settings.bracketSize} onChange={(e) => set("bracketSize", Number(e.target.value) as Settings["bracketSize"])}>
                      <option value={64}>64 teams</option>
                      <option value={68}>68 teams (First Four)</option>
                      <option value={76}>76 teams (expanded)</option>
                    </select>
                  </div>
                  <div className="field" style={{ flex: 1 }}>
                    <label>Roster limit</label>
                    <select className="select" value={settings.rosterMax} onChange={(e) => set("rosterMax", Number(e.target.value))}>
                      <option value={13}>13 scholarships</option>
                      <option value={15}>15 roster spots</option>
                    </select>
                  </div>
                  <div className="field" style={{ flex: 1 }}>
                    <label>Recruiting AI</label>
                    <select className="select" value={settings.recruitingDifficulty} onChange={(e) => set("recruitingDifficulty", Number(e.target.value) as Settings["recruitingDifficulty"])}>
                      <option value={1}>Easy</option>
                      <option value={2}>Normal</option>
                      <option value={3}>Hard</option>
                    </select>
                  </div>
                </div>
                <button className="btn btn-dark btn-lg mt-8" disabled={creating} onClick={create}>
                  {creating ? "Building 365 programs…" : `Take the ${selected.name} job`}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function luminance(h: string): number {
  const x = h.replace("#", "");
  return (0.2126 * parseInt(x.slice(0, 2), 16) + 0.7152 * parseInt(x.slice(2, 4), 16) + 0.0722 * parseInt(x.slice(4, 6), 16)) / 255;
}
