import { useMemo, useState, type CSSProperties, type ReactNode } from "react";
import { Link } from "react-router-dom";
import type { League, Player, Team } from "../../engine/types";
import { grade, gradeClass } from "../../engine/ratings";
import { cls, contrast, luminance, heroColors } from "../util";
import { Icon } from "./Icons";
import { Face } from "./Face";
import { teamMaybe } from "../../engine/core";

// ---------------- team visuals ----------------
const SHAPES = ["circle", "shield", "round", "hex", "circle", "shield"] as const;
type Shape = (typeof SHAPES)[number];
const OUTER: Record<Shape, string> = {
  circle: "M50 1a49 49 0 1 0 0.01 0z",
  shield: "M50 1.5L95 13.5V49c0 27-19.5 43.5-45 50.5C24.5 92.5 5 76 5 49V13.5z",
  round: "M27 2h46a25 25 0 0 1 25 25v46a25 25 0 0 1-25 25H27A25 25 0 0 1 2 73V27A25 25 0 0 1 27 2z",
  hex: "M50 1l44 24.5v49L50 99 6 74.5v-49z",
};
const INNER: Record<Shape, string> = {
  circle: "M50 8a42 42 0 1 0 0.01 0z",
  shield: "M50 9l37.5 10V49c0 22.5-16 36.5-37.5 43C28.5 85.5 12.5 71.5 12.5 49V19z",
  round: "M28 9.5h44A18.5 18.5 0 0 1 90.5 28v44A18.5 18.5 0 0 1 72 90.5H28A18.5 18.5 0 0 1 9.5 72V28A18.5 18.5 0 0 1 28 9.5z",
  hex: "M50 9.5l36.5 20.3v40.4L50 90.5 13.5 70.2V29.8z",
};
const logoCache = new Map<string, { p: string; ring: string; text: string; shape: Shape }>();
function logoStyle(abbrev: string, colors: [string, string]) {
  const key = `${abbrev}${colors[0]}${colors[1]}`;
  let v = logoCache.get(key);
  if (!v) {
    const [p, s] = colors;
    const ring = contrast(p, s) >= 1.4 ? s : luminance(p) < 0.4 ? "#ffffff" : "#111827";
    const text = contrast(s, p) >= 3 ? s : contrast("#ffffff", p) >= contrast("#0f1726", p) ? "#ffffff" : "#0f1726";
    let h = 0;
    for (const ch of abbrev) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
    v = { p, ring, text, shape: SHAPES[h % SHAPES.length] };
    logoCache.set(key, v);
  }
  return v;
}

export function Logo({ team, size = 28 }: { team: Pick<Team, "abbrev" | "colors"> | undefined; size?: number }) {
  if (!team)
    return (
      <span className="logo" style={{ width: size, height: size }}>
        <svg viewBox="0 0 100 100">
          <path d={OUTER.circle} fill="var(--border-strong)" />
          <text x="50" y="50" dy="0.35em" textAnchor="middle" fontSize="44" fill="var(--muted)" className="logo-text">
            ?
          </text>
        </svg>
      </span>
    );
  const st = logoStyle(team.abbrev, team.colors);
  const shape: Shape = size < 22 ? "circle" : st.shape;
  const n = team.abbrev.length;
  const fs = n <= 2 ? 46 : n === 3 ? 37 : 29;
  const ty = shape === "shield" ? 47 : 50;
  return (
    <span className="logo" style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100" aria-hidden>
        <path d={OUTER[shape]} fill={st.ring} />
        <path d={INNER[shape]} fill={st.p} />
        {size >= 36 && <path d={INNER[shape]} fill="none" stroke={st.ring} strokeOpacity={0.4} strokeWidth={1.6} transform="translate(50 50) scale(0.88) translate(-50 -50)" />}
        <text x="50" y={ty} dy="0.35em" textAnchor="middle" fontSize={fs} fill={st.text} className="logo-text">
          {team.abbrev}
        </text>
      </svg>
    </span>
  );
}

/** CSS variables that paint a hero banner in a team's colors. */
export function heroStyle(colors: [string, string]): CSSProperties {
  const h = heroColors(colors);
  return { ["--h1" as string]: h.h1, ["--hd" as string]: h.hd, ["--h2" as string]: h.h2 };
}

export function TeamLink({ L, tid, short, logo = true, size = 22, rank, season }: { L: League; tid: number | null | undefined; short?: boolean; logo?: boolean; size?: number; rank?: number | null; season?: number }) {
  const t = teamMaybe(L, tid);
  if (!t) return <span className="faint">-</span>;
  return (
    <span className="team-cell">
      {logo && <Logo team={t} size={size} />}
      <Link to={`/l/${L.id}/team/${t.id}${season !== undefined ? `?season=${season}` : ""}`}>
        {rank ? <span className="faint small" style={{ fontWeight: 650 }}>{rank} </span> : null}
        {short ? t.short : t.name}
      </Link>
    </span>
  );
}

export function PlayerLink({ L, p, face = false, size = 30, colors, meta }: { L: League; p: Pick<Player, "id" | "first" | "last" | "faceSeed" | "race">; face?: boolean; size?: number; colors?: [string, string]; meta?: ReactNode }) {
  return (
    <span className="player-cell">
      {face && <Face seed={p.faceSeed} race={p.race} colors={colors} size={size} />}
      <span>
        <Link to={`/l/${L.id}/player/${p.id}`}>
          {p.first} {p.last}
        </Link>
        {meta && <span className="meta">{meta}</span>}
      </span>
    </span>
  );
}

// ---------------- ratings ----------------
export function Grade({ v, letter = true, lg, md }: { v: number; letter?: boolean; lg?: boolean; md?: boolean }) {
  return <span className={cls("grade", gradeClass(v), lg && "lg", md && "md")}>{letter ? grade(v) : Math.round(v)}</span>;
}
/** A rating as a heat cell: one hue, stronger for higher values; the number stays in text color. */
export function Rating({ v }: { v: number }) {
  const h = Math.max(0, Math.min(1, (v - 52) / 36)) ** 1.25;
  return (
    <span className={cls("rt", v < 40 && "lo", v >= 75 && "hi")} style={{ ["--h" as string]: h.toFixed(3) }}>
      {Math.round(v)}
    </span>
  );
}
export const GRADE_COLOR: Record<string, string> = { "g-a": "var(--ga)", "g-b": "var(--gb)", "g-c": "var(--gc)", "g-d": "var(--gd)", "g-f": "var(--gf)" };
export function gradeColor(v: number): string {
  return GRADE_COLOR[gradeClass(v)];
}
const STAR = "M12 2.6l2.85 6.05 6.6.78-4.88 4.55 1.28 6.52L12 17.3l-5.85 3.2 1.28-6.52L2.55 9.43l6.6-.78z";
export function Stars({ n, max = 5, lg }: { n: number; max?: number; lg?: boolean }) {
  const out: ReactNode[] = [];
  for (let i = 0; i < max; i++) {
    const f = Math.max(0, Math.min(1, n - i));
    out.push(
      <span key={i} style={{ position: "relative", display: "inline-block" }}>
        <svg viewBox="0 0 24 24">
          <path d={STAR} className="star-off" />
        </svg>
        {f > 0 && (
          <svg viewBox="0 0 24 24" style={{ position: "absolute", inset: 0, clipPath: f >= 1 ? undefined : "inset(0 50% 0 0)" }}>
            <path d={STAR} className="star-on" />
          </svg>
        )}
      </span>,
    );
  }
  return (
    <span className={cls("stars", lg && "lg")} title={`${n} star${n === 1 ? "" : "s"}`}>
      {out}
    </span>
  );
}

/** Ring gauge for a 0-100 value (OVR/POT, interest, security). */
export function Gauge({ v, label, size = 72, color, text, track }: { v: number; label?: ReactNode; size?: number; color?: string; text?: ReactNode; track?: string }) {
  const r = 44;
  const c = 2 * Math.PI * r;
  const f = Math.max(0, Math.min(1, v / 100));
  return (
    <span className="gauge" style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke={track ?? "rgba(127,127,127,0.22)"} strokeWidth="8" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color ?? gradeColor(v)} strokeWidth="8" strokeLinecap="round" strokeDasharray={`${c * f} ${c}`} />
      </svg>
      <span className="gv">
        <b style={{ fontSize: size * 0.34 }}>{text ?? Math.round(v)}</b>
        {label && <small>{label}</small>}
      </span>
    </span>
  );
}

/** Rating bar with value and letter grade. */
export function RatingBar({ name, v }: { name: ReactNode; v: number }) {
  return (
    <div className="rbar">
      <span className="nm">{name}</span>
      <span className="v">{Math.round(v)}</span>
      <Grade v={v} />
      <div className="track">
        <span style={{ width: `${Math.max(2, Math.min(100, v))}%`, background: `rgba(var(--heat), ${(0.45 + 0.55 * Math.max(0, Math.min(1, (v - 30) / 60))).toFixed(2)})` }} />
      </div>
    </div>
  );
}

export function FormStrip({ results, n = 5 }: { results: boolean[]; n?: number }) {
  const r = results.slice(0, n);
  const pad = Math.max(0, n - r.length);
  return (
    <span className="form">
      {r.map((w, i) => (
        <span key={i} className={w ? "w" : "l"}>
          {w ? "W" : "L"}
        </span>
      ))}
      {Array.from({ length: pad }, (_, i) => (
        <span key={`o${i}`} className="o">
          -
        </span>
      ))}
    </span>
  );
}

export function Tile({ label, value, foot, icon, style, children }: { label: ReactNode; value?: ReactNode; foot?: ReactNode; icon?: string; style?: CSSProperties; children?: ReactNode }) {
  return (
    <div className="tile" style={style}>
      <div className="label">
        {icon && <Icon name={icon} size={13} />}
        {label}
      </div>
      {value !== undefined && <div className="value">{value}</div>}
      {children}
      {foot && <div className="foot">{foot}</div>}
    </div>
  );
}

export function Trophy({ size = 13 }: { size?: number }) {
  return (
    <span className="trophy-ic" style={{ width: size + 9, height: size + 9 }}>
      <Icon name="awards" size={size} />
    </span>
  );
}

export function Pos({ p }: { p: string }) {
  return <span className="pos">{p}</span>;
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

export function PageHead({ title, sub, right, logo, eyebrow }: { title: ReactNode; sub?: ReactNode; right?: ReactNode; logo?: ReactNode; eyebrow?: ReactNode }) {
  return (
    <div className="page-head">
      {logo}
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
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
