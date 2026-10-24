import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useLeague, useSim, runSim, stopSim, type SimTarget } from "../store";
import { currentDateLabel, PHASE_LABEL, seasonLabel, team } from "../../engine/core";
import { currentRank } from "../../engine/rankings";
import { curSeason } from "../../engine/play";
import { heroColors, inkOn } from "../util";
import { Icon } from "./Icons";
import { Logo } from "./common";
import { GlobalSearch } from "./Search";
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
        <span className="ic">
          <Icon name="play" />
        </span>
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
        <div className="bold">Simulating…</div>
        <div className="small" style={{ opacity: 0.7 }}>
          {sim.label}
        </div>
      </div>
      <button className="btn btn-sm" onClick={stopSim}>
        Stop
      </button>
    </div>
  );
}

const TOAST_MS = 8000;

function ResultToast() {
  const L = useLeague();
  const sim = useSim();
  const [shown, setShown] = useState<number | null>(null);
  const gid = sim.lastResult?.gid ?? null;
  const seen = useRef<number | null>(gid);
  // pop up once per new result, not again on later sims or phase changes
  useEffect(() => {
    if (sim.running) setShown(null);
    else if (gid !== null && seen.current !== gid) {
      seen.current = gid;
      setShown(gid);
    }
  }, [gid, sim.running]);
  useEffect(() => {
    if (shown === null) return;
    const t = setTimeout(() => setShown(null), TOAST_MS);
    return () => clearTimeout(t);
  }, [shown]);
  if (shown === null || sim.running) return null;
  const g = L.games.find((x) => x.id === shown);
  if (!g) return null;
  const userHome = g.home === L.userTid;
  const us = userHome ? g.hs : g.as;
  const them = userHome ? g.as : g.hs;
  const opp = team(L, userHome ? g.away : g.home);
  const won = us > them;
  return (
    <div className="toast" key={shown} style={{ ["--toast-c" as string]: won ? "var(--ga)" : "var(--gf)", ["--toast-ms" as string]: `${TOAST_MS}ms` }}>
      <div className="row" style={{ gap: 12 }}>
        <Logo team={opp} size={34} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className={`result ${won ? "good" : "bad"}`}>
            {won ? "W" : "L"} {us}-{them}
            {g.ot ? <span style={{ fontSize: 15, marginLeft: 4 }}>{g.ot > 1 ? `${g.ot}OT` : "OT"}</span> : null}
          </div>
          <div className="small muted ellipsis">
            {g.neutral ? "vs" : userHome ? "vs" : "at"} {opp.name}
            {g.event ? ` · ${g.event}` : ""}
          </div>
        </div>
        <Link className="btn btn-sm" to={`/l/${L.id}/game/${g.id}?watch=1`} onClick={() => setShown(null)}>
          <Icon name="play" size={11} /> Watch
        </Link>
        <Link className="btn btn-sm btn-primary" to={`/l/${L.id}/game/${g.id}`} onClick={() => setShown(null)}>
          Box Score
        </Link>
        <button className="btn btn-ghost btn-sm" onClick={() => setShown(null)} aria-label="Dismiss">
          <Icon name="x" size={13} />
        </button>
      </div>
      <div className="toast-timer" />
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
  const rank = currentRank(L, t.id);
  const unread = L.news.filter((n) => n.user && !n.read).length;
  useEffect(() => {
    const root = document.documentElement;
    const h = heroColors(t.colors);
    root.style.setProperty("--accent", h.h1);
    root.style.setProperty("--accent-text", "#ffffff");
    root.style.setProperty("--team1", t.colors[0]);
    root.style.setProperty("--team2", h.h2);
    root.style.setProperty("--team-dark", h.hd);
    root.style.setProperty("--accent-ink-d", inkOn(t.colors[0], "#111723"));
    root.style.setProperty("--accent-ink-l", inkOn(t.colors[0], "#ffffff", 4));
    document.title = `${t.name} · Hardwood Dynasty`;
  }, [t]);
  const badges: Record<string, number> = { inbox: unread, coach: L.jobOffers.length };
  return (
    <div className="app">
      <aside className="sidebar">
        <Link to="/" className="brand">
          <span className="brand-mark">
            <Icon name="crown" size={19} />
          </span>
          <div style={{ minWidth: 0 }}>
            <div className="brand-name">Hardwood Dynasty</div>
            <small className="ellipsis">{L.name}</small>
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
        <div className="sidebar-foot">
          <NavLink to={`/l/${L.id}/guide`} className={({ isActive }) => `side-icon${isActive ? " active" : ""}`} title="How to play">
            <Icon name="ball" />
          </NavLink>
          <NavLink to={`/l/${L.id}/settings`} className={({ isActive }) => `side-icon${isActive ? " active" : ""}`} title="Settings">
            <Icon name="settings" />
          </NavLink>
          <Link to="/" className="side-icon" title="All leagues">
            <Icon name="exit" />
          </Link>
          <div className="side-phase">
            {seasonLabel(L.season)}
            <br />
            {PHASE_LABEL[L.phase]}
          </div>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <Link to={`/l/${L.id}/team/${t.id}`} style={{ display: "flex" }}>
            <Logo team={t} size={44} />
          </Link>
          <div style={{ minWidth: 0 }}>
            <div className="team-name ellipsis">
              {rank ? <span className="rk">#{rank}</span> : null}
              {t.name} {t.mascot}
            </div>
            <div className="sub">
              <b>
                {s.w}-{s.l}
              </b>{" "}
              · {s.cw}-{s.cl} {L.conferences[t.cid].short} · {PHASE_LABEL[L.phase]}
            </div>
          </div>
          <div className="spacer" />
          <GlobalSearch />
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
