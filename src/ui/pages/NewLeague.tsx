import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createLeague, DEFAULT_SETTINGS, teamCatalog } from "../../engine/league";
import type { Settings } from "../../engine/types";
import { prestigeTier, prestigeStars } from "../../engine/ratings";
import { heroStyle, Logo, Seg, Stars } from "../components/common";
import { Icon } from "../components/Icons";
import { expectations } from "../../engine/coaches";
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
  const exp = expectations(selected.prestige);
  const difficulty = selected.prestige >= 85 ? ["Defend a dynasty", "Expectations are sky-high"] : selected.prestige >= 65 ? ["Contender", "Win now, recruit elite players"] : selected.prestige >= 45 ? ["Mid-major climb", "Win your league, then move up"] : ["From nowhere to Blue Blood", "The hardest, most rewarding path"];
  return (
    <div className="home-wrap">
      <div style={{ maxWidth: 1320, margin: "0 auto", padding: "26px 28px 40px", position: "relative" }}>
        <div className="row mb-16" style={{ gap: 14 }}>
          <Link to="/" className="ghost-light" style={{ height: 38, padding: "0 14px" }}>
            ‹ Back
          </Link>
          <div>
            <div className="hero-kicker" style={{ color: "var(--l-muted)", opacity: 1 }}>
              New league
            </div>
            <div className="home-title" style={{ fontSize: 40 }}>
              Choose your program
            </div>
          </div>
        </div>
        <div className="grid newleague-grid" style={{ alignItems: "start" }}>
          <div className="card">
            <div className="filter-bar">
              <div className="search-box">
                <Icon name="search" size={14} />
                <input className="input" placeholder="Search programs…" value={q} onChange={(e) => setQ(e.target.value)} />
              </div>
              <select className="select" value={conf} onChange={(e) => setConf(e.target.value)}>
                <option value="all">All conferences</option>
                {cat.conferences.map((c) => (
                  <option key={c.slug} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
              <Seg
                options={[
                  { key: "prestige", label: "By prestige" },
                  { key: "name", label: "A-Z" },
                ]}
                value={sort}
                onChange={setSort}
              />
              <span className="spacer" />
              <button className="btn btn-sm" onClick={() => pick((t) => t.prestige < 30)}>
                <Icon name="bolt" size={13} /> Random low-major
              </button>
              <button className="btn btn-sm" onClick={() => pick(() => true)}>
                Random
              </button>
            </div>
            <div style={{ maxHeight: "calc(100vh - 210px)", minHeight: 420, overflowY: "auto" }}>
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Program ({list.length})</th>
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
                          <Logo team={t} size={28} />
                          <b>{t.name}</b> <span className="muted">{t.mascot}</span>
                        </span>
                      </td>
                      <td className="muted">{confName(t.conf)}</td>
                      <td>
                        <Stars n={prestigeStars(t.prestige)} />
                      </td>
                      <td>
                        <span className="badge">{prestigeTier(t.prestige)}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="col gap-16">
            <div className="hero-banner" style={heroStyle(selected.colors)}>
              <div className="hero-inner" style={{ gap: 18 }}>
                <Logo team={selected} size={96} />
                <div style={{ minWidth: 0 }}>
                  <div className="hero-kicker">{cat.conferences.find((c) => c.slug === selected.conf)?.name}</div>
                  <div className="hero-title" style={{ fontSize: 38, marginTop: 4 }}>
                    {selected.name}
                  </div>
                  <div className="hero-sub">
                    {selected.mascot} · {selected.city}, {selected.state}
                  </div>
                  <div className="row-wrap" style={{ marginTop: 10, gap: 8 }}>
                    <span className="chip-light">
                      <Stars n={prestigeStars(selected.prestige)} /> {prestigeTier(selected.prestige)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="hero-stats">
                <div>
                  <div className="label">The job</div>
                  <div className="value" style={{ fontSize: 16 }}>
                    {difficulty[0]}
                  </div>
                  <div className="small" style={{ opacity: 0.75 }}>
                    {difficulty[1]}
                  </div>
                </div>
                <div>
                  <div className="label">Year-one goal</div>
                  <div className="value" style={{ fontSize: 16 }}>
                    {exp.goal}
                  </div>
                </div>
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
                  <div className="field" style={{ flex: 1.3 }}>
                    <label>League name</label>
                    <input className="input" value={name} onChange={(e) => setName(e.target.value)} />
                  </div>
                </div>
                <div className="grid g2" style={{ gap: 10 }}>
                  <label className="check">
                    <input type="checkbox" checked={settings.portal} onChange={(e) => set("portal", e.target.checked)} /> Transfer portal
                  </label>
                  <label className="check">
                    <input type="checkbox" checked={settings.nil} onChange={(e) => set("nil", e.target.checked)} /> NIL deals
                  </label>
                  <label className="check">
                    <input type="checkbox" checked={settings.canBeFired} onChange={(e) => set("canBeFired", e.target.checked)} /> You can be fired
                  </label>
                  <label className="check">
                    <input type="checkbox" checked={settings.injuries} onChange={(e) => set("injuries", e.target.checked)} /> Injuries
                  </label>
                </div>
                <div className="row">
                  <div className="field" style={{ flex: 1 }}>
                    <label>NCAA field</label>
                    <select className="select" value={settings.bracketSize} onChange={(e) => set("bracketSize", Number(e.target.value) as Settings["bracketSize"])}>
                      <option value={64}>64 teams</option>
                      <option value={68}>68 (First Four)</option>
                      <option value={76}>76 (expanded)</option>
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
                <button className="cta mt-8" style={{ justifyContent: "center", width: "100%" }} disabled={creating} onClick={create}>
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
