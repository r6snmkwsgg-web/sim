import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useLeague, useSim, runSim, stopSim, getWatchGuard, setWatchGuard, useWatchGuard, type SimTarget } from "../store";
import { currentDateLabel, PHASE_LABEL, seasonLabel, team } from "../../engine/core";
import { currentRank } from "../../engine/rankings";
import { curSeason } from "../../engine/play";
import { heroColors, inkOn } from "../util";
import { Icon } from "./Icons";
import { Logo } from "./common";
import { GlobalSearch } from "./Search";
import { PORTAL_ROUNDS, advanceBlocker, isDayPhase } from "../../engine/advance";
import { nextGame } from "../helpers";
import type { League } from "../../engine/types";
import { HUBS, hubPages, hubTarget, locate, rememberPage, type NavHub } from "../nav";
import { useCloudStatus } from "../cloud";
import { clearMoments, popMoment, useMoments } from "../moments";
import { Face } from "./Face";
import { cloudLine } from "./CloudCard";

interface Action {
  target: SimTarget;
  label: string;
  sub?: string;
  /** label for narrow screens */
  short?: string;
}

function actionsFor(L: League): { main: Action; more: Action[] } {
  switch (L.phase) {
    case "preseason":
      return { main: { target: "advance", label: "Start Season", short: "Start" }, more: [{ target: "advance", label: "Start the regular season", sub: "Lock in redshirts and tip off" }] };
    case "regular":
      return {
        main: { target: "nextGame", label: "Play Next Game", short: "Play" },
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
        main: { target: "day", label: "Sim Day", short: "Sim Day" },
        more: [
          { target: "day", label: "Sim one day" },
          { target: "nextGame", label: "Play next game" },
          { target: "selection", label: "Sim to Selection Sunday" },
        ],
      };
    case "selection":
      return { main: { target: "advance", label: "Start Tournaments", short: "Start" }, more: [{ target: "advance", label: "Begin the NCAA Tournament, NIT and CBI" }] };
    case "ncaa":
      return {
        main: { target: "day", label: "Sim Day", short: "Sim Day" },
        more: [
          { target: "day", label: "Sim one day" },
          { target: "nextGame", label: "Play next game" },
          { target: "endPostseason", label: "Sim to end of postseason" },
        ],
      };
    case "seasonEnd":
      return { main: { target: "advance", label: "Coaching Carousel", short: "Next" }, more: [{ target: "advance", label: "Proceed to the coaching carousel", sub: "Firings, hirings and job offers" }] };
    case "carousel":
      return { main: { target: "advance", label: "Draft & Departures", short: "Next" }, more: [{ target: "advance", label: "Proceed to the NBA Draft", sub: "Seniors graduate, early entries leave" }] };
    case "draft":
      return { main: { target: "advance", label: "Open Transfer Portal", short: "Next" }, more: [{ target: "advance", label: "Open the transfer portal" }] };
    case "portal":
      return {
        main: { target: "advance", label: `Next Portal Window (${L.portalRound}/${PORTAL_ROUNDS})`, short: `Window ${L.portalRound}/${PORTAL_ROUNDS}` },
        more: [
          { target: "advance", label: "Advance one portal window", sub: "AI programs make their moves; commitments happen" },
          { target: "endPortal", label: "Sim to Signing Day" },
        ],
      };
    case "signing":
      return { main: { target: "advance", label: `Start ${seasonLabel(L.season + 1)}`, short: "Start" }, more: [{ target: "advance", label: "Begin the new season", sub: "Players develop, recruits enroll, new schedule" }] };
  }
}

/** Does the user's team have a game coming that can be watched? */
export function canWatchNext(L: League): boolean {
  if (!isDayPhase(L)) return false;
  if (nextGame(L, L.userTid)) return true;
  return L.brackets.some((b) => b.champion === null && b.games.some((g) => g.winner === null && (g.a === L.userTid || g.b === L.userTid)));
}

/** Sim to the user's next game without revealing the result, then open it in the live viewer. */
export function useWatchNext(): () => Promise<void> {
  const L = useLeague();
  const nav = useNavigate();
  return async () => {
    const rank = currentRank(L, L.userTid);
    const { userGameId } = await runSim("nextGame", { quiet: true });
    if (userGameId === null) return;
    const g = L.games.find((x) => x.id === userGameId);
    if (!g) return;
    const won = g.home === L.userTid ? g.hs > g.as : g.as > g.hs;
    setWatchGuard({ gid: g.id, won, conf: g.type === "conf", rank });
    nav(`/l/${L.id}/game/${g.id}?watch=1`);
  };
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
  const watchNext = useWatchNext();
  const canWatch = canWatchNext(L);
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
    <div ref={ref} style={{ position: "relative", display: "flex", gap: 6 }}>
      {canWatch && (
        <button className="watch-btn" disabled={sim.running} onClick={() => void watchNext()} title="Play your next game and watch it live">
          <Icon name="tv" size={15} /> <span className="lbl-long">Watch</span>
        </button>
      )}
      <button className="play-btn" disabled={sim.running} onClick={() => go(main)}>
        <span className="ic">
          <Icon name="play" />
        </span>
        <span className="lbl-long">{main.label}</span>
        <span className="lbl-short">{main.short ?? main.label}</span>
      </button>
      <button className="play-btn play-more" disabled={sim.running} onClick={() => setOpen(!open)} aria-label="More sim options">
        <Icon name="chevron" />
      </button>
      {open && (
        <div className="menu">
          {canWatch && (
            <>
              <button
                className="menu-item"
                onClick={() => {
                  setOpen(false);
                  void watchNext();
                }}
              >
                Watch next game live
                <small>Your game plays out on a court with a live box score</small>
              </button>
              <div className="menu-sep" />
            </>
          )}
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

const CONFETTI = Array.from({ length: 36 }, (_, i) => ({
  left: (i * 37) % 100,
  delay: ((i * 53) % 100) / 100,
  dur: 1.8 + ((i * 29) % 10) / 10,
  rot: (i * 47) % 360,
  c: i % 3,
}));

/** Full-screen celebrations (and gut punches) after a sim. */
function MomentOverlay() {
  const L = useLeague();
  const guard = useWatchGuard();
  const { queue, more } = useMoments();
  const nav = useNavigate();
  useEffect(() => () => clearMoments(), [L.id]);
  useEffect(() => {
    if (!queue.length || guard) return;
    const k = (e: KeyboardEvent) => {
      if (e.key === "Enter" || e.key === "Escape" || e.key === " ") {
        e.preventDefault();
        popMoment();
      }
    };
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [queue.length, guard]);
  if (guard || !queue.length) return null;
  const m = queue[0];
  const t = team(L, m.tid);
  const h = heroColors(t.colors);
  const p = m.pid !== undefined ? L.players.find((x) => x.id === m.pid) : undefined;
  return (
    <div className="moment-wrap" onClick={(e) => e.target === e.currentTarget && popMoment()}>
      <div className={`moment${m.sad ? " sad" : ""}`} style={{ ["--m1" as string]: h.h1, ["--m2" as string]: h.h2, ["--md" as string]: h.hd }}>
        {m.celebrate && (
          <div className="confetti" aria-hidden>
            {CONFETTI.map((c, i) => (
              <i key={i} className={`c${c.c}`} style={{ left: `${c.left}%`, animationDelay: `${c.delay}s`, animationDuration: `${c.dur}s`, transform: `rotate(${c.rot}deg)` }} />
            ))}
          </div>
        )}
        <div className="moment-kicker">{m.kicker}</div>
        <div className="moment-art">
          {p ? <Face seed={p.faceSeed} race={p.race} colors={t.colors} size={120} frame={false} /> : null}
          {m.logos?.map((tid, i) => (
            <span key={tid} className={i === 0 ? "lead" : "other"}>
              <Logo team={team(L, tid)} size={i === 0 ? (p ? 64 : 96) : 48} />
            </span>
          ))}
        </div>
        <div className="moment-title">{m.title}</div>
        {m.sub && <div className="moment-sub">{m.sub}</div>}
        <div className="moment-actions">
          {m.link && (
            <button
              className="btn btn-glass"
              onClick={() => {
                const to = m.link!.to;
                popMoment();
                nav(to);
              }}
            >
              {m.link.label}
            </button>
          )}
          <button className="btn btn-white" autoFocus onClick={popMoment}>
            {queue.length > 1 ? `Next (${queue.length - 1} more)` : "Continue"}
          </button>
        </div>
        {queue.length === 1 && more > 0 && <div className="moment-more">+{more} more in your inbox</div>}
      </div>
    </div>
  );
}

/** Cloud save status at a glance; opens Settings. */
function CloudDot({ lid }: { lid: string }) {
  const st = useCloudStatus();
  return (
    <Link to={`/l/${lid}/settings`} className={`side-icon cloud-dot ${st.state}`} title={cloudLine(st)}>
      <Icon name="cloud" />
    </Link>
  );
}

/** The five sections: a slim rail on desktop, a tab bar on phones. */
function HubLinks({ L, active, badges, className }: { L: League; active: NavHub | null; badges: Record<string, number>; className: string }) {
  return (
    <nav className={className}>
      {HUBS.map((h) => (
        <Link key={h.key} to={`/l/${L.id}/${hubTarget(L, h)}`} className={`hub-item${active?.key === h.key ? " active" : ""}`}>
          <span className="hub-ic">
            <Icon name={h.icon} size={20} />
            {badges[h.key] ? <span className="hub-badge">{badges[h.key]}</span> : null}
          </span>
          <span className="hub-label">{h.short}</span>
        </Link>
      ))}
    </nav>
  );
}

/** The current section's pages as tabs, with a way back from detail screens. */
function SubNav({ L, rest, search }: { L: League; rest: string; search: string }) {
  const nav = useNavigate();
  const spot = locate(L, rest, search);
  const hub = spot.hub;
  useEffect(() => {
    if (hub && spot.page) rememberPage(hub.key, spot.page.to);
  }, [hub, spot.page]);
  if (!hub) return null;
  const pages = hubPages(L, hub);
  const unread = L.news.filter((n) => n.user && !n.read).length;
  const count: Record<string, number> = { inbox: unread, coach: L.jobOffers.length };
  const back = () => {
    const idx = (window.history.state as { idx?: number } | null)?.idx ?? 0;
    if (idx > 0) nav(-1);
    else nav(`/l/${L.id}/${hubTarget(L, hub)}`);
  };
  return (
    <div className="subnav">
      {spot.detail && (
        <button className="subnav-back" onClick={back} title="Back">
          <Icon name="back" size={15} /> Back
        </button>
      )}
      <span className="subnav-hub">{hub.label}</span>
      <div className="subnav-tabs">
        {pages.map((p) => (
          <Link key={p.to} to={`/l/${L.id}/${p.to}`} className={`subnav-tab${spot.page === p ? " active" : ""}`}>
            {p.label}
            {count[p.to] ? <span className="nav-badge">{count[p.to]}</span> : null}
          </Link>
        ))}
      </div>
    </div>
  );
}

export function Layout({ children }: { children: ReactNode }) {
  const L = useLeague();
  const t = team(L, L.userTid);
  const s = curSeason(t);
  const liveRank = currentRank(L, t.id);
  const unread = L.news.filter((n) => n.user && !n.read).length;
  // hide the result of a game that's being watched
  const guard = useWatchGuard();
  const loc = useLocation();
  // leaving the game being watched reveals the result (checked only when the page changes)
  useEffect(() => {
    const g = getWatchGuard();
    if (g && !(loc.pathname.endsWith(`/game/${g.gid}`) && loc.search.includes("watch=1"))) setWatchGuard(null);
  }, [loc]);
  // each new screen starts at the top
  const contentRef = useRef<HTMLElement>(null);
  useEffect(() => {
    contentRef.current?.scrollTo(0, 0);
  }, [loc.pathname]);
  const rec = guard
    ? { w: s.w - (guard.won ? 1 : 0), l: s.l - (guard.won ? 0 : 1), cw: s.cw - (guard.conf && guard.won ? 1 : 0), cl: s.cl - (guard.conf && !guard.won ? 1 : 0) }
    : { w: s.w, l: s.l, cw: s.cw, cl: s.cl };
  const rank = guard ? guard.rank : liveRank;
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
  const rest = loc.pathname.replace(/^\/l\/[^/]+\/?/, "");
  const spot = locate(L, rest, loc.search);
  const badges: Record<string, number> = { home: unread, team: L.jobOffers.length };
  return (
    <div className="app">
      <aside className="rail">
        <Link to="/" className="rail-brand" title={`Hardwood Dynasty · ${L.name} (all leagues)`}>
          <Icon name="crown" size={19} />
        </Link>
        <HubLinks L={L} active={spot.hub} badges={badges} className="rail-hubs" />
        <div className="rail-foot">
          <CloudDot lid={L.id} />
          <NavLink to={`/l/${L.id}/guide`} className={({ isActive }) => `side-icon${isActive ? " active" : ""}`} title="How to play">
            <Icon name="ball" />
          </NavLink>
          <NavLink to={`/l/${L.id}/settings`} className={({ isActive }) => `side-icon${isActive ? " active" : ""}`} title="Settings">
            <Icon name="settings" />
          </NavLink>
          <Link to="/" className="side-icon" title="All leagues">
            <Icon name="exit" />
          </Link>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <Link to={`/l/${L.id}/team/${t.id}`} className="topbar-logo" title="Team page">
            <Logo team={t} size={44} />
          </Link>
          <div style={{ minWidth: 0 }}>
            <div className="team-name ellipsis">
              {rank ? <span className="rk">#{rank}</span> : null}
              <span className="lbl-long">
                {t.name} {t.mascot}
              </span>
              <span className="lbl-short">{t.short}</span>
            </div>
            <div className="sub ellipsis">
              <b>
                {rec.w}-{rec.l}
              </b>{" "}
              · {rec.cw}-{rec.cl} {L.conferences[t.cid].short}
              <span className="lbl-long"> · {PHASE_LABEL[L.phase]}</span>
            </div>
          </div>
          <div className="spacer" />
          <GlobalSearch />
          <Link
            to={`/l/${L.id}/targets`}
            className={`points-pill${L.recruitPts === 0 ? " empty" : ""}`}
            title="Coaching points left this week. Spend them on recruits or game prep. They reset every Monday."
          >
            <Icon name="bolt" size={15} />
            <b>{L.recruitPts}</b>
            <span className="lbl-long">pts</span>
          </Link>
          <div className="date">
            <b>{currentDateLabel(L)}</b>
            {seasonLabel(L.season)} season
          </div>
          <PlayMenu />
        </header>
        <SubNav L={L} rest={rest} search={loc.search} />
        <main className="content" ref={contentRef}>
          <div className="page">{children}</div>
        </main>
      </div>
      <HubLinks L={L} active={spot.hub} badges={badges} className="tabbar" />
      <SimOverlay />
      <ResultToast />
      <MomentOverlay />
    </div>
  );
}
