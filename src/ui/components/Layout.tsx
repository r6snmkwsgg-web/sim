import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useLeague, useSim, runSim, stopSim, type SimTarget } from "../store";
import { currentDateLabel, PHASE_LABEL, seasonLabel, team } from "../../engine/core";
import { currentRank } from "../../engine/rankings";
import { curSeason } from "../../engine/play";
import { accentFor, textOn } from "../util";
import { Icon } from "./Icons";
import { Logo } from "./common";
import { PORTAL_ROUNDS, advanceBlocker } from "../../engine/advance";
import type { League } from "../../engine/types";

interface Action {
  target: SimTarget;
  label: string;
  sub?: string;
}

function actionsFor(L: League): { main: Action; more: Action[] } {
  switch (L.phase) {
    case "preseason":
      return { main: { target: "advance", label: "Start Season" }, more: [{ target: "advance", label: "Start the regular season", sub: "Lock in redshirts and tip off" }] };
    case "regular":
      return {
        main: { target: "nextGame", label: "Play Next Game" },
        more: [
          { target: "nextGame", label: "Play next game", sub: "Sim until your next game is final" },
          { target: "day", label: "Sim one day" },
          { target: "week", label: "Sim one week" },
          { target: "endRegular", label: "Sim to end of regular season", sub: "Through the last regular-season day" },
          { target: "selection", label: "Sim to Selection Sunday", sub: "Includes conference tournaments" },
        ],
      };
    case "confTourney":
      return {
        main: { target: "day", label: "Sim Day" },
        more: [
          { target: "day", label: "Sim one day" },
          { target: "nextGame", label: "Play next game" },
          { target: "selection", label: "Sim to Selection Sunday" },
        ],
      };
    case "selection":
      return { main: { target: "advance", label: "Start Tournaments" }, more: [{ target: "advance", label: "Begin the NCAA Tournament, NIT and CBI" }] };
    case "ncaa":
      return {
        main: { target: "day", label: "Sim Day" },
        more: [
          { target: "day", label: "Sim one day" },
          { target: "nextGame", label: "Play next game" },
          { target: "endPostseason", label: "Sim to end of postseason" },
        ],
      };
    case "seasonEnd":
      return { main: { target: "advance", label: "Coaching Carousel" }, more: [{ target: "advance", label: "Proceed to the coaching carousel", sub: "Firings, hirings and job offers" }] };
    case "carousel":
      return { main: { target: "advance", label: "Draft & Departures" }, more: [{ target: "advance", label: "Proceed to the NBA Draft", sub: "Seniors graduate, early entries leave" }] };
    case "draft":
      return { main: { target: "advance", label: "Open Transfer Portal" }, more: [{ target: "advance", label: "Open the transfer portal" }] };
    case "portal":
      return {
        main: { target: "advance", label: `Next Portal Window (${L.portalRound}/${PORTAL_ROUNDS})` },
        more: [
          { target: "advance", label: "Advance one portal window", sub: "AI programs make their moves; commitments happen" },
          { target: "endPortal", label: "Sim to Signing Day" },
        ],
      };
    case "signing":
      return { main: { target: "advance", label: `Start ${seasonLabel(L.season + 1)}` }, more: [{ target: "advance", label: "Begin the new season", sub: "Players develop, recruits enroll, new schedule" }] };
  }
}

function PlayMenu() {
  const L = useLeague();
  const sim = useSim();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, []);
  const { main, more } = actionsFor(L);
  const go = async (a: Action) => {
    setOpen(false);
    if (a.target === "advance") {
      const block = advanceBlocker(L);
      if (block) {
        alert(block);
        return;
      }
      if (L.phase === "signing") {
        const over = Math.max(0, rosterCount(L) - L.settings.rosterMax);
        if (over > 0 && !confirm(`Your roster is ${over} over the limit. The lowest-rated players will be released automatically. Continue?`)) {
          nav(`/l/${L.id}/roster`);
          return;
        }
      }
    }
    const before = L.phase;
    await runSim(a.target);
    // route the user to the relevant page after phase changes
    if (L.phase !== before) {
      const to: Partial<Record<League["phase"], string>> = {
        selection: "tournaments",
        seasonEnd: "season-review",
        carousel: "coach",
        draft: "draft",
        portal: "portal",
        signing: "signing",
        preseason: "",
        regular: "",
      };
      const dest = to[L.phase];
      if (dest !== undefined) nav(`/l/${L.id}/${dest}`);
    }
  };
  return (
    <div ref={ref} style={{ position: "relative", display: "flex" }}>
      <button className="play-btn" disabled={sim.running} onClick={() => go(main)}>
        <Icon name="play" />
        {main.label}
      </button>
      <button className="play-btn play-more" disabled={sim.running} onClick={() => setOpen(!open)} aria-label="More sim options">
        <Icon name="chevron" />
      </button>
      {open && (
        <div className="menu">
          {more.map((a, i) => (
            <button key={i} className="menu-item" onClick={() => go(a)}>
              {a.label}
              {a.sub && <small>{a.sub}</small>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function rosterCount(L: League): number {
  // current roster plus signed incoming recruits
  let n = 0;
  for (const p of L.players) {
    if (p.status === "active" && p.tid === L.userTid) n++;
    else if (p.recruit && p.recruit.kind === "hs" && p.recruit.stage === "signed" && p.recruit.committedTo === L.userTid) n++;
  }
  return n;
}

function SimOverlay() {
  const sim = useSim();
  if (!sim.running) return null;
  return (
    <div className="sim-overlay">
      <div className="spinner" />
      <div style={{ flex: 1 }}>
        <div className="bold">Simulating</div>
        <div className="small" style={{ opacity: 0.8 }}>
          {sim.label}
        </div>
      </div>
      <button className="btn btn-sm" onClick={stopSim}>
        Stop
      </button>
    </div>
  );
}

function ResultToast() {
  const L = useLeague();
  const sim = useSim();
  const [shown, setShown] = useState<number | null>(null);
  const gid = sim.lastResult?.gid ?? null;
  useEffect(() => {
    if (gid !== null) {
      setShown(gid);
      const t = setTimeout(() => setShown(null), 9000);
      return () => clearTimeout(t);
    }
  }, [gid, sim.running]);
  if (shown === null || sim.running) return null;
  const g = L.games.find((x) => x.id === shown);
  if (!g) return null;
  const userHome = g.home === L.userTid;
  const us = userHome ? g.hs : g.as;
  const them = userHome ? g.as : g.hs;
  const opp = team(L, userHome ? g.away : g.home);
  const won = us > them;
  return (
    <div className="toast">
      <div className="row">
        <Logo team={opp} size={30} />
        <div style={{ flex: 1 }}>
          <div className={won ? "good bold" : "bad bold"} style={{ fontSize: 16 }}>
            {won ? "Win" : "Loss"} {us}-{them}
            {g.ot ? ` (${g.ot > 1 ? g.ot : ""}OT)` : ""}
          </div>
          <div className="small muted">
            {g.neutral ? "vs" : userHome ? "vs" : "at"} {opp.name}
            {g.event ? ` · ${g.event}` : ""}
          </div>
        </div>
        <Link className="btn btn-sm" to={`/l/${L.id}/game/${g.id}`} onClick={() => setShown(null)}>
          Box Score
        </Link>
        <button className="btn btn-ghost btn-sm" onClick={() => setShown(null)}>
          ✕
        </button>
      </div>
    </div>
  );
}

const NAV: { head: string; items: { to: string; label: string; icon: string; phases?: League["phase"][] }[] }[] = [
  {
    head: "Program",
    items: [
      { to: "", label: "Dashboard", icon: "home" },
      { to: "inbox", label: "Inbox", icon: "inbox" },
      { to: "roster", label: "Roster", icon: "roster" },
      { to: "tactics", label: "Tactics", icon: "tactics" },
      { to: "rotation", label: "Rotation", icon: "rotation" },
      { to: "practice", label: "Practice", icon: "practice" },
      { to: "schedule", label: "Schedule", icon: "schedule" },
      { to: "coach", label: "Coach & Jobs", icon: "coach" },
    ],
  },
  {
    head: "Recruiting",
    items: [
      { to: "recruiting", label: "Recruiting Board", icon: "recruit" },
      { to: "targets", label: "My Targets", icon: "star" },
      { to: "classes", label: "Class Rankings", icon: "rankings" },
      { to: "portal", label: "Transfer Portal", icon: "portal" },
    ],
  },
  {
    head: "League",
    items: [
      { to: "scores", label: "Scores", icon: "scores" },
      { to: "standings", label: "Standings", icon: "standings" },
      { to: "rankings", label: "Rankings", icon: "rankings" },
      { to: "tournaments", label: "Tournaments", icon: "bracket" },
      { to: "stats", label: "Stats", icon: "stats" },
      { to: "awards", label: "Awards", icon: "awards" },
    ],
  },
  {
    head: "History",
    items: [
      { to: "history", label: "League History", icon: "history" },
      { to: "program", label: "Program History", icon: "team" },
      { to: "records", label: "Record Book", icon: "records" },
      { to: "draft", label: "NBA Draft", icon: "draft" },
      { to: "transfers", label: "Transfers", icon: "portal" },
    ],
  },
];

export function Layout({ children }: { children: ReactNode }) {
  const L = useLeague();
  const t = team(L, L.userTid);
  const s = curSeason(t);
  const accent = accentFor(t.colors);
  const rank = currentRank(L, t.id);
  const unread = L.news.filter((n) => n.user && !n.read).length;
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty("--accent", accent);
    root.style.setProperty("--accent-text", textOn(accent));
    root.style.setProperty("--accent-soft", `${accent}1f`);
    root.style.setProperty("--accent-bright", t.colors[0] === accent ? "#ffffff" : t.colors[0]);
    document.title = `${t.name} · Hardwood Dynasty`;
  }, [accent, t]);
  const badges: Record<string, number> = { inbox: unread, coach: L.jobOffers.length };
  return (
    <div className="app">
      <aside className="sidebar">
        <Link to="/" className="brand" style={{ textDecoration: "none" }}>
          <Icon name="crown" size={22} />
          <div>
            Hardwood Dynasty
            <small>{L.name}</small>
          </div>
        </Link>
        {NAV.map((sec) => (
          <div className="nav-section" key={sec.head}>
            <div className="nav-head">{sec.head}</div>
            {sec.items.map((it) => (
              <NavLink key={it.to} end={it.to === ""} to={`/l/${L.id}/${it.to}`} className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
                <Icon name={it.icon} />
                {it.label}
                {badges[it.to] ? <span className="nav-badge">{badges[it.to]}</span> : null}
              </NavLink>
            ))}
          </div>
        ))}
        <div className="nav-section">
          <NavLink to={`/l/${L.id}/settings`} className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
            <Icon name="settings" />
            Settings
          </NavLink>
          <Link to="/" className="nav-item">
            <Icon name="exit" />
            All Leagues
          </Link>
        </div>
        <div className="sidebar-foot">
          {seasonLabel(L.season)} · {PHASE_LABEL[L.phase]}
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <Logo team={t} size={42} />
          <div>
            <div className="team-name">
              {rank ? <span style={{ opacity: 0.8, fontWeight: 600 }}>#{rank} </span> : null}
              {t.name} {t.mascot}
            </div>
            <div className="sub">
              {s.w}-{s.l} ({s.cw}-{s.cl} {L.conferences[t.cid].short}) · {PHASE_LABEL[L.phase]}
            </div>
          </div>
          <div className="spacer" />
          <div className="date">
            <b>{currentDateLabel(L)}</b>
            {seasonLabel(L.season)} season
          </div>
          <PlayMenu />
        </header>
        <main className="content">
          <div className="page">{children}</div>
        </main>
      </div>
      <SimOverlay />
      <ResultToast />
    </div>
  );
}
