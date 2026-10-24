import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { seasonLabel } from "../../engine/core";
import { Card, PageHead, Seg } from "../components/common";
import { KIND_COLORS } from "../helpers";
import type { NewsKind } from "../../engine/types";

const KINDS: { k: NewsKind | "all"; label: string }[] = [
  { k: "all", label: "All" },
  { k: "game", label: "Games" },
  { k: "recruit", label: "Recruiting" },
  { k: "portal", label: "Portal" },
  { k: "injury", label: "Injuries" },
  { k: "award", label: "Awards" },
  { k: "job", label: "Jobs" },
  { k: "league", label: "League" },
];

export function Inbox() {
  const L = useLeague();
  const [scope, setScope] = useState<"mine" | "all">("mine");
  const [kind, setKind] = useState<NewsKind | "all">("all");
  const items = L.news.filter((n) => (scope === "all" || n.user) && (kind === "all" || n.kind === kind));
  useEffect(() => {
    // mark as read after viewing
    const t = setTimeout(() => {
      if (L.news.some((n) => !n.read)) mutate((LL) => LL.news.forEach((n) => (n.read = true)));
    }, 1500);
    return () => clearTimeout(t);
  }, [L]);
  let lastSeason = -1;
  return (
    <div>
      <PageHead
        title="Inbox"
        sub={`${L.news.filter((n) => n.user && !n.read).length} unread`}
        right={
          <div className="row">
            <Seg
              options={[
                { key: "mine", label: "My program" },
                { key: "all", label: "Everything" },
              ]}
              value={scope}
              onChange={setScope}
            />
          </div>
        }
      />
      <div className="row-wrap mb-12">
        {KINDS.map((k) => (
          <button key={k.k} className={`chip ${kind === k.k ? "on" : ""}`} onClick={() => setKind(k.k)}>
            {k.k !== "all" && <span style={{ width: 8, height: 8, borderRadius: 4, background: KIND_COLORS[k.k] }} />}
            {k.label}
          </button>
        ))}
      </div>
      <Card flush>
        {items.length === 0 && <div className="empty">Nothing here.</div>}
        {items.slice(0, 400).map((n) => {
          const head = n.season !== lastSeason;
          lastSeason = n.season;
          return (
            <div key={n.id}>
              {head && (
                <div className="tiny muted bold" style={{ padding: "8px 14px", background: "var(--panel-2)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  {seasonLabel(n.season)}
                </div>
              )}
              <div className={`news-item ${n.read ? "" : "unread"}`}>
                <span className="news-kind" style={{ background: KIND_COLORS[n.kind] }} />
                <div style={{ flex: 1 }}>
                  {n.gid ? <Link to={`/l/${L.id}/game/${n.gid}`}>{n.text}</Link> : n.pid ? <Link to={`/l/${L.id}/player/${n.pid}`}>{n.text}</Link> : n.tid !== undefined && !n.user ? <Link to={`/l/${L.id}/team/${n.tid}`}>{n.text}</Link> : n.text}
                </div>
                <span className="tiny faint nowrap">{n.dateLabel}</span>
              </div>
            </div>
          );
        })}
      </Card>
    </div>
  );
}
