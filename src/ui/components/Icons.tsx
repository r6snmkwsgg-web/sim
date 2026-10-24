// Small inline icon set (stroke icons, 24x24 viewBox).

const P: Record<string, string> = {
  home: "M3 11l9-8 9 8M5 10v10h5v-6h4v6h5V10",
  inbox: "M3 13h5l2 3h4l2-3h5M5 5h14l2 8v6H3v-6z",
  roster: "M16 11a3 3 0 100-6 3 3 0 000 6zM8 11a3 3 0 100-6 3 3 0 000 6zM2 20c0-3 3-5 6-5s6 2 6 5M14 15.5c.6-.3 1.3-.5 2-.5 3 0 6 2 6 5",
  tactics: "M4 4h16v16H4zM12 4v16M4 12h16M8 8l2 2M16 16l-2-2",
  rotation: "M4 6h12M4 12h16M4 18h8M18 4v4M14 16l3 3 4-5",
  practice: "M6 4v16M18 4v16M6 12h12M3 8v8M21 8v8",
  schedule: "M4 6h16v14H4zM4 10h16M8 3v5M16 3v5",
  standings: "M4 20V10M10 20V4M16 20v-8M22 20H2",
  rankings: "M12 3l2.5 5.5L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.5-.5z",
  bracket: "M3 5h5v4H3zM3 15h5v4H3zM8 7h4v10H8M12 12h4M16 10h5v4h-5z",
  recruit: "M11 4a4 4 0 110 8 4 4 0 010-8zM3 21c0-4 4-6 8-6M17 14v7M13.5 17.5h7",
  portal: "M7 7h10v10H7zM3 12h4M17 12h4M12 3v4M12 17v4",
  stats: "M4 19h16M7 16V9M12 16V5M17 16v-4",
  awards: "M8 4h8v5a4 4 0 01-8 0zM5 5h3v3a3 3 0 01-3-3zM19 5h-3v3a3 3 0 003-3zM12 13v4M8 20h8M10 17h4",
  history: "M3 12a9 9 0 109-9 9 9 0 00-7 3.5M3 4v4h4M12 7v5l3 3",
  records: "M6 3h12v18l-6-4-6 4z",
  coach: "M12 3a4 4 0 110 8 4 4 0 010-8zM5 21v-2a5 5 0 015-5h4a5 5 0 015 5v2M9 14l3 4 3-4",
  draft: "M5 3h14v18H5zM9 7h6M9 11h6M9 15h4",
  settings: "M12 9a3 3 0 100 6 3 3 0 000-6zM19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 01-4 0v-.1a1.7 1.7 0 00-1.1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 010-4h.1a1.7 1.7 0 001.5-1.1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 014 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 010 4h-.1a1.7 1.7 0 00-1.5 1z",
  play: "M7 4l13 8-13 8z",
  chevron: "M6 9l6 6 6-6",
  team: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
  scores: "M4 5h16v14H4zM9 5v14M15 9h2M15 13h2M6 9h1M6 13h1",
  exit: "M15 4h4v16h-4M10 8l-4 4 4 4M6 12h11",
  star: "M12 3l2.5 5.5L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.5-.5z",
  ball: "M12 3a9 9 0 100 18 9 9 0 000-18zM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18",
  crown: "M3 8l4 4 5-7 5 7 4-4-2 11H5z",
  fire: "M12 3c1 3 4 5 4 9a4 4 0 01-8 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-2-5 0-8zM6 14a6 6 0 0012 0",
  shield: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
  trend: "M3 17l6-6 4 4 8-8M15 7h6v6",
  money: "M3 6h18v12H3zM12 9a3 3 0 100 6 3 3 0 000-6zM6 9v.01M18 15v.01",
  plus: "M12 5v14M5 12h14",
  upload: "M12 16V4M7 9l5-5 5 5M4 20h16",
  phone: "M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z",
  eye: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 9a3 3 0 100 6 3 3 0 000-6z",
  plane: "M2 16l20-8-20-8 4 8zM6 8h8",
  pin: "M12 21s-7-6-7-11a7 7 0 0114 0c0 5-7 11-7 11zM12 7a3 3 0 100 6 3 3 0 000-6z",
  whistle: "M3 10h10l3-3h5v6a6 6 0 01-6 6H9a6 6 0 01-6-6zM9 13h.01",
  calendar: "M4 6h16v14H4zM4 10h16M8 3v5M16 3v5",
  bolt: "M13 2L4 14h7l-1 8 9-12h-7z",
  heart: "M12 20s-8-5-8-11a4.5 4.5 0 018-3 4.5 4.5 0 018 3c0 6-8 11-8 11z",
  check: "M5 12l5 5 9-10",
  search: "M11 4a7 7 0 100 14 7 7 0 000-14zM20 20l-4-4",
  x: "M6 6l12 12M18 6L6 18",
};

export function Icon({ name, size = 16, className }: { name: keyof typeof P | string; size?: number; className?: string }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d={P[name] ?? P.ball} />
    </svg>
  );
}
