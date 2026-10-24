import { useMemo, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import type { League, Player, Team } from "../../engine/types";
import { grade, gradeClass } from "../../engine/ratings";
import { textOn, cls } from "../util";
import { Face } from "./Face";
import { teamMaybe } from "../../engine/core";

// ---------------- team visuals ----------------
export function Logo({ team, size = 28 }: { team: Pick<Team, "abbrev" | "colors"> | undefined; size?: number }) {
  if (!team) return <span className="logo" style={{ width: size, height: size, background: "#9ca3af" }} />;
  const [bg, fg0] = team.colors;
  const fg = Math.abs(lumDiff(bg, fg0)) > 0.25 ? fg0 : textOn(bg);
  const n = team.abbrev.length;
  const fs = size * (n <= 1 ? 0.55 : n === 2 ? 0.42 : n === 3 ? 0.33 : 0.27);
  return (
    <span className="logo" style={{ width: size, height: size, background: bg, color: fg, fontSize: fs }}>
      {team.abbrev}
    </span>
  );
}
function lumDiff(a: string, b: string): number {
  const l = (h: string) => {
    const x = h.replace("#", "");
    const r = parseInt(x.slice(0, 2), 16) / 255;
    const g = parseInt(x.slice(2, 4), 16) / 255;
    const bb = parseInt(x.slice(4, 6), 16) / 255;
    return 0.2126 * r + 0.7152 * g + 0.0722 * bb;
  };
  return l(a) - l(b);
}

export function TeamLink({ L, tid, short, logo = true, size = 22, rank, season }: { L: League; tid: number | null | undefined; short?: boolean; logo?: boolean; size?: number; rank?: number | null; season?: number }) {
  const t = teamMaybe(L, tid);
  if (!t) return <span className="faint">-</span>;
  return (
    <span className="team-cell">
      {logo && <Logo team={t} size={size} />}
      <Link to={`/l/${L.id}/team/${t.id}${season !== undefined ? `?season=${season}` : ""}`}>
        {rank ? <span className="muted small">#{rank} </span> : null}
        {short ? t.short : t.name}
      </Link>
    </span>
  );
}

export function PlayerLink({ L, p, face = false, size = 30, colors }: { L: League; p: Pick<Player, "id" | "first" | "last" | "faceSeed" | "race">; face?: boolean; size?: number; colors?: [string, string] }) {
  return (
    <span className="player-cell">
      {face && <Face seed={p.faceSeed} race={p.race} colors={colors} size={size} />}
      <Link to={`/l/${L.id}/player/${p.id}`}>
        {p.first} {p.last}
      </Link>
    </span>
  );
}

// ---------------- ratings ----------------
export function Grade({ v, letter = true }: { v: number; letter?: boolean }) {
  return <span className={cls("grade", gradeClass(v))}>{letter ? grade(v) : Math.round(v)}</span>;
}
export function Rating({ v }: { v: number }) {
  return <span className={cls("rt", gradeClass(v))}>{Math.round(v)}</span>;
}
export function Stars({ n, max = 5 }: { n: number; max?: number }) {
  const full = Math.floor(n);
  const half = n - full >= 0.5;
  return (
    <span className="stars" title={`${n} stars`}>
      {"★".repeat(full)}
      {half ? "⯪" : ""}
      <span className="off">{"★".repeat(Math.max(0, max - full - (half ? 1 : 0)))}</span>
    </span>
  );
}

// ---------------- layout bits ----------------
export function Card({ title, sub, right, children, flush, className }: { title?: ReactNode; sub?: ReactNode; right?: ReactNode; children: ReactNode; flush?: boolean; className?: string }) {
  return (
    <div className={cls("card", className)}>
      {(title || right) && (
        <div className="card-h">
          <div>
            {typeof title === "string" ? <h2>{title}</h2> : title}
            {sub && <div className="sub">{sub}</div>}
          </div>
          <div className="spacer" />
          {right}
        </div>
      )}
      <div className={cls("card-b", flush && "flush")}>{children}</div>
    </div>
  );
}

export function PageHead({ title, sub, right, logo }: { title: ReactNode; sub?: ReactNode; right?: ReactNode; logo?: ReactNode }) {
  return (
    <div className="page-head">
      {logo}
      <div>
        <h1>{title}</h1>
        {sub && <div className="sub">{sub}</div>}
      </div>
      <div className="spacer" />
      {right}
    </div>
  );
}

export function Tabs<T extends string>({ tabs, value, onChange, small }: { tabs: { key: T; label: ReactNode }[]; value: T; onChange: (k: T) => void; small?: boolean }) {
  return (
    <div className={cls("tabs", small && "small")}>
      {tabs.map((t) => (
        <button key={t.key} className={cls("tab", value === t.key && "active")} onClick={() => onChange(t.key)}>
          {t.label}
        </button>
      ))}
    </div>
  );
}

export function Seg<T extends string | number>({ options, value, onChange }: { options: { key: T; label: ReactNode }[]; value: T; onChange: (k: T) => void }) {
  return (
    <div className="seg">
      {options.map((o) => (
        <button key={String(o.key)} className={value === o.key ? "on" : ""} onClick={() => onChange(o.key)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function SeasonSelect({ L, value, onChange, from }: { L: League; value: number; onChange: (s: number) => void; from?: number }) {
  const opts: number[] = [];
  for (let s = L.season; s >= (from ?? L.startSeason); s--) opts.push(s);
  return (
    <select className="select" value={value} onChange={(e) => onChange(Number(e.target.value))}>
      {opts.map((s) => (
        <option key={s} value={s}>
          {s}-{String((s + 1) % 100).padStart(2, "0")}
        </option>
      ))}
    </select>
  );
}

export function Bar({ value, max, thin, color }: { value: number; max: number; thin?: boolean; color?: string }) {
  const w = Math.max(0, Math.min(100, (100 * value) / Math.max(1e-9, max)));
  return (
    <div className={cls("bar", thin && "thin")}>
      <span style={{ width: `${w}%`, background: color }} />
    </div>
  );
}

export function Meter({ value, color }: { value: number; color: string }) {
  return (
    <div className="meter">
      <span style={{ width: `${Math.max(0, Math.min(100, value))}%`, background: color }} />
    </div>
  );
}

export function Modal({ title, children, onClose, footer }: { title: ReactNode; children: ReactNode; onClose: () => void; footer?: ReactNode }) {
  return (
    <div className="overlay" onMouseDown={onClose}>
      <div className="modal" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-h">
          <h2>{title}</h2>
          <div className="spacer" />
          <button className="btn btn-ghost btn-sm" onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="modal-b">{children}</div>
        {footer && <div className="modal-f">{footer}</div>}
      </div>
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="empty">{children}</div>;
}

// ---------------- sortable table ----------------
export interface Col<T> {
  key: string;
  label: ReactNode;
  title?: string;
  render: (row: T, i: number) => ReactNode;
  sort?: (row: T) => number | string;
  num?: boolean;
  center?: boolean;
  defaultDesc?: boolean;
  width?: number;
}

export function Table<T>({
  cols,
  rows,
  rowKey,
  initialSort,
  initialDesc,
  onRowClick,
  rowClass,
  compact,
  limit,
  empty,
  foot,
}: {
  cols: Col<T>[];
  rows: T[];
  rowKey: (r: T) => string | number;
  initialSort?: string;
  initialDesc?: boolean;
  onRowClick?: (r: T) => void;
  rowClass?: (r: T) => string | undefined;
  compact?: boolean;
  limit?: number;
  empty?: ReactNode;
  foot?: ReactNode;
}) {
  const [sortKey, setSortKey] = useState<string | undefined>(initialSort);
  const [desc, setDesc] = useState<boolean>(initialDesc ?? true);
  const [page, setPage] = useState(0);
  const sorted = useMemo(() => {
    const c = cols.find((x) => x.key === sortKey);
    if (!c?.sort) return rows;
    const f = c.sort;
    const out = rows.slice().sort((a, b) => {
      const x = f(a);
      const y = f(b);
      if (typeof x === "number" && typeof y === "number") return desc ? y - x : x - y;
      return desc ? String(y).localeCompare(String(x)) : String(x).localeCompare(String(y));
    });
    return out;
  }, [rows, cols, sortKey, desc]);
  const pages = limit ? Math.max(1, Math.ceil(sorted.length / limit)) : 1;
  const pg = Math.min(page, pages - 1);
  const shown = limit ? sorted.slice(pg * limit, pg * limit + limit) : sorted;
  return (
    <>
      <div className="tbl-wrap">
        <table className={cls("tbl", compact && "compact")}>
          <thead>
            <tr>
              {cols.map((c) => (
                <th
                  key={c.key}
                  title={c.title}
                  className={cls(c.num && "n", c.center && "c", c.sort && "sortable")}
                  style={c.width ? { width: c.width } : undefined}
                  onClick={() => {
                    if (!c.sort) return;
                    if (sortKey === c.key) setDesc(!desc);
                    else {
                      setSortKey(c.key);
                      setDesc(c.defaultDesc ?? !!c.num);
                    }
                    setPage(0);
                  }}
                >
                  {c.label}
                  {sortKey === c.key && <span className="arrow">{desc ? "▼" : "▲"}</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {shown.map((r, i) => (
              <tr key={rowKey(r)} className={cls(onRowClick && "clickable", rowClass?.(r))} onClick={onRowClick ? () => onRowClick(r) : undefined}>
                {cols.map((c) => (
                  <td key={c.key} className={cls(c.num && "n", c.center && "c")}>
                    {c.render(r, pg * (limit ?? 0) + i)}
                  </td>
                ))}
              </tr>
            ))}
            {!rows.length && (
              <tr>
                <td colSpan={cols.length} className="empty">
                  {empty ?? "Nothing to show"}
                </td>
              </tr>
            )}
          </tbody>
          {foot && <tfoot>{foot}</tfoot>}
        </table>
      </div>
      {limit && pages > 1 && (
        <div className="row" style={{ padding: "10px 12px" }}>
          <span className="muted small">
            {pg * limit + 1}-{Math.min(sorted.length, (pg + 1) * limit)} of {sorted.length}
          </span>
          <div className="spacer" />
          <button className="btn btn-sm" disabled={pg === 0} onClick={() => setPage(pg - 1)}>
            ‹ Prev
          </button>
          <button className="btn btn-sm" disabled={pg >= pages - 1} onClick={() => setPage(pg + 1)}>
            Next ›
          </button>
        </div>
      )}
    </>
  );
}
