// Navigation map: five sections ("hubs"), each with its own pages. The
// sidebar and the phone tab bar show the hubs; each page shows its hub's
// pages as tabs, so related screens are always one click apart.

import type { League } from "../engine/types";

export interface NavPage {
  to: string;
  label: string;
  /** extra words the search box should match */
  alias?: string;
  /** only offered in some phases */
  when?: (L: League) => boolean;
}

export interface NavHub {
  key: string;
  label: string;
  short: string;
  icon: string;
  pages: NavPage[];
}

const OFFSEASON: League["phase"][] = ["seasonEnd", "carousel", "draft", "portal", "signing"];

export const HUBS: NavHub[] = [
  {
    key: "home",
    label: "Home",
    short: "Home",
    icon: "home",
    pages: [
      { to: "", label: "Dashboard", alias: "home overview" },
      { to: "inbox", label: "Inbox", alias: "news messages" },
      { to: "season-review", label: "Season Review", alias: "recap summary", when: (L) => OFFSEASON.includes(L.phase) },
      { to: "guide", label: "How to Play", alias: "help guide tutorial" },
      { to: "settings", label: "Settings", alias: "options export backup theme" },
    ],
  },
  {
    key: "team",
    label: "My Team",
    short: "Team",
    icon: "roster",
    pages: [
      { to: "roster", label: "Roster", alias: "players lineup" },
      { to: "schedule", label: "Schedule", alias: "games results" },
      { to: "tactics", label: "Tactics", alias: "strategy offense defense tempo" },
      { to: "rotation", label: "Rotation", alias: "minutes starters" },
      { to: "practice", label: "Practice", alias: "development training" },
      { to: "signing", label: "Next Season", alias: "signing day roster limit", when: (L) => ["draft", "portal", "signing"].includes(L.phase) },
      { to: "coach", label: "Coach & Jobs", alias: "career job offers security" },
    ],
  },
  {
    key: "recruit",
    label: "Recruiting",
    short: "Recruit",
    icon: "recruit",
    pages: [
      { to: "recruiting", label: "Board", alias: "recruiting board prospects high school" },
      { to: "targets", label: "My Targets", alias: "recruits" },
      { to: "portal", label: "Transfer Portal", alias: "transfers" },
      { to: "classes", label: "Class Rankings", alias: "recruiting classes" },
    ],
  },
  {
    key: "league",
    label: "League",
    short: "League",
    icon: "league",
    pages: [
      { to: "scores", label: "Scores", alias: "games results today" },
      { to: "standings", label: "Standings", alias: "conference" },
      { to: "rankings", label: "Rankings", alias: "ap poll top 25 power" },
      { to: "tournaments", label: "Tournaments", alias: "bracket ncaa march madness nit" },
      { to: "stats", label: "Stats", alias: "leaders" },
      { to: "awards", label: "Awards", alias: "player of the year all-america" },
    ],
  },
  {
    key: "history",
    label: "History",
    short: "History",
    icon: "history",
    pages: [
      { to: "history", label: "League History", alias: "champions past seasons" },
      { to: "program", label: "Program History", alias: "my program past teams" },
      { to: "records", label: "Record Book", alias: "records" },
      { to: "draft", label: "NBA Draft", alias: "draft picks" },
      { to: "transfers", label: "Transfers", alias: "transfer log" },
    ],
  },
];

export function hubPages(L: League, hub: NavHub): NavPage[] {
  return hub.pages.filter((p) => !p.when || p.when(L));
}

export interface NavSpot {
  hub: NavHub | null;
  /** the hub page this screen belongs to, if it is one */
  page: NavPage | null;
  /** a detail screen (a team, player or game) reached from somewhere else */
  detail: boolean;
}

/** Where a path (the part after /l/:lid/) sits in the navigation. */
export function locate(L: League, rest: string, search = ""): NavSpot {
  const [head, id] = rest.split("/");
  for (const hub of HUBS) {
    const page = hub.pages.find((p) => p.to === (head ?? ""));
    if (page) return { hub, page, detail: false };
  }
  const by = (key: string) => HUBS.find((h) => h.key === key)!;
  if (head === "team") {
    const tid = Number(id);
    if (tid === L.userTid) {
      const hist = by("history");
      return search.includes("tab=history") ? { hub: hist, page: hist.pages.find((p) => p.to === "program")!, detail: false } : { hub: by("team"), page: null, detail: true };
    }
    return { hub: by("league"), page: null, detail: true };
  }
  if (head === "player") {
    const p = L.players.find((x) => x.id === Number(id));
    if (p && (p.status === "recruit" || p.status === "portal")) return { hub: by("recruit"), page: null, detail: true };
    if (p && p.tid === L.userTid && p.status === "active") return { hub: by("team"), page: null, detail: true };
    return { hub: by("league"), page: null, detail: true };
  }
  if (head === "game") {
    const g = L.games.find((x) => x.id === Number(id));
    if (g && (g.home === L.userTid || g.away === L.userTid)) return { hub: by("team"), page: null, detail: true };
    return { hub: by("league"), page: null, detail: true };
  }
  return { hub: null, page: null, detail: false };
}

// the last page opened in each hub, so a hub button returns you to where you were
const lastPage = new Map<string, string>();

export function rememberPage(hubKey: string, to: string) {
  lastPage.set(hubKey, to);
}

export function hubTarget(L: League, hub: NavHub): string {
  const pages = hubPages(L, hub);
  const last = lastPage.get(hub.key);
  if (last !== undefined && pages.some((p) => p.to === last)) return last;
  return pages[0].to;
}
