import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLeague } from "../store";
import { Logo } from "./common";
import { Icon } from "./Icons";
import { team } from "../../engine/core";
import { ratingsHidden } from "../../engine/recruiting";
import { HUBS, hubPages } from "../nav";

interface Hit {
  key: string;
  label: string;
  sub: string;
  to: string;
  tid?: number;
  icon?: string;
}

export function GlobalSearch() {
  const L = useLeague();
  const nav = useNavigate();
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [sel, setSel] = useState(0);
  // phones show a search button that opens the box over the top bar
  const [expanded, setExpanded] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setExpanded(false);
      }
    };
    const k = (e: KeyboardEvent) => {
      if ((e.key === "/" || (e.key === "k" && (e.metaKey || e.ctrlKey))) && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        inputRef.current?.focus();
        setOpen(true);
      }
    };
    document.addEventListener("mousedown", h);
    document.addEventListener("keydown", k);
    return () => {
      document.removeEventListener("mousedown", h);
      document.removeEventListener("keydown", k);
    };
  }, []);
  const hits = useMemo<Hit[]>(() => {
    const s = q.trim().toLowerCase();
    if (s.length < 2) return [];
    const out: Hit[] = [];
    // pages first: "standings", "bracket", "draft"...
    for (const h of HUBS) {
      for (const p of hubPages(L, h)) {
        if (out.length >= 3) break;
        const words = `${p.label} ${p.alias ?? ""}`.toLowerCase();
        if (words.split(/\s+/).some((w) => w.startsWith(s)) || words.includes(s)) out.push({ key: `pg${h.key}${p.to}`, label: p.label, sub: `Go to page · ${h.label}`, to: `/l/${L.id}/${p.to}`, icon: h.icon });
      }
    }
    for (const t of L.teams) {
      if (`${t.name} ${t.mascot} ${t.abbrev}`.toLowerCase().includes(s)) out.push({ key: `t${t.id}`, label: `${t.name} ${t.mascot}`, sub: L.conferences[t.cid].short, to: `/l/${L.id}/team/${t.id}`, tid: t.id });
      if (out.length >= 8) break;
    }
    for (const p of L.players) {
      if (out.length >= 12) break;
      if (!`${p.first} ${p.last}`.toLowerCase().includes(s)) continue;
      const sub =
        p.status === "recruit" ? `${ratingsHidden(L, p) ? "Unrated" : `${p.recruit?.stars}★`} recruit · ${p.pos}` : p.status === "portal" ? `Transfer portal · ${p.pos}` : p.tid !== null ? `${team(L, p.tid).short} · ${p.pos}` : p.pos;
      out.push({ key: `p${p.id}`, label: `${p.first} ${p.last}`, sub, to: `/l/${L.id}/player/${p.id}`, tid: p.tid ?? p.recruit?.committedTo ?? undefined });
    }
    return out;
  }, [q, L]);
  const go = (h: Hit) => {
    setOpen(false);
    setExpanded(false);
    setQ("");
    inputRef.current?.blur();
    nav(h.to);
  };
  return (
    <div ref={ref} className={`search-wrap${expanded ? " open" : ""}`} style={{ position: "relative" }}>
      <button
        className="search-btn"
        aria-label="Search"
        onClick={() => {
          setExpanded(true);
          setOpen(true);
          setTimeout(() => inputRef.current?.focus(), 0);
        }}
      >
        <Icon name="search" size={17} />
      </button>
      <span className="search-ic">
        <Icon name="search" size={14} />
      </span>
      <kbd className="search-kbd">/</kbd>
      <input
        ref={inputRef}
        className="input search-glass"
        placeholder="Search teams, players, pages"
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          setOpen(true);
          setSel(0);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={(e) => {
          if (e.key === "ArrowDown") setSel((x) => Math.min(hits.length - 1, x + 1));
          else if (e.key === "ArrowUp") setSel((x) => Math.max(0, x - 1));
          else if (e.key === "Enter" && hits[sel]) go(hits[sel]);
          else if (e.key === "Escape") {
            setOpen(false);
            setExpanded(false);
            (e.target as HTMLInputElement).blur();
          }
        }}

      />
      {open && hits.length > 0 && (
        <div className="menu" style={{ left: 0, right: "auto", width: 360 }}>
          {hits.map((h, i) => (
            <button key={h.key} className="menu-item row" style={{ background: i === sel ? "var(--panel-3)" : undefined }} onMouseEnter={() => setSel(i)} onClick={() => go(h)}>
              {h.tid !== undefined && h.tid !== null ? (
                <Logo team={team(L, h.tid)} size={22} />
              ) : h.icon ? (
                <span className="search-page-ic">
                  <Icon name={h.icon} size={14} />
                </span>
              ) : (
                <span style={{ width: 22 }} />
              )}
              <span style={{ flex: 1 }}>
                {h.label}
                <small>{h.sub}</small>
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
