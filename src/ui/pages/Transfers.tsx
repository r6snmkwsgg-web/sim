import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { team } from "../../engine/core";
import type { TransferMove } from "../../engine/types";
import { Card, Empty, Grade, PageHead, Seg, Stars, Table, TeamLink, type Col } from "../components/common";

export function Transfers() {
  const L = useLeague();
  const log = [...(L.transferLog ?? []), ...(L.phase === "portal" ? L.transfers : [])];
  const years = [...new Set(log.map((m) => m.season))].sort((a, b) => b - a);
  const [year, setYear] = useState<number>(years[0] ?? L.season + 1);
  const [scope, setScope] = useState<"all" | "mine">("all");
  const rows = log.filter((m) => m.season === year && (scope === "all" || m.from === L.userTid || m.to === L.userTid));
  const cols: Col<TransferMove>[] = [
    { key: "name", label: "Player", render: (m) => <Link to={`/l/${L.id}/player/${m.pid}`}>{m.name}</Link>, sort: (m) => m.name },
    { key: "stars", label: "Stars", render: (m) => <Stars n={m.stars} />, sort: (m) => m.stars, num: true },
    { key: "ovr", label: "OVR", render: (m) => <Grade v={m.ovr} />, sort: (m) => m.ovr, num: true },
    { key: "from", label: "From", render: (m) => <TeamLink L={L} tid={m.from} size={18} />, sort: (m) => team(L, m.from).name },
    { key: "to", label: "To", render: (m) => (m.to !== null ? <TeamLink L={L} tid={m.to} size={18} /> : <span className="muted">Undecided</span>), sort: (m) => (m.to !== null ? team(L, m.to).name : "") },
    {
      key: "dir",
      label: "",
      render: (m) => {
        if (m.to === null) return null;
        const d = team(L, m.to).prestige - team(L, m.from).prestige;
        return d > 15 ? <span className="badge good">Moving up</span> : d < -15 ? <span className="badge">Moving down</span> : null;
      },
    },
  ];
  return (
    <div>
      <PageHead
        title="Transfers"
        sub="Every completed transfer, kept for good."
        right={
          <div className="row">
            <Seg
              options={[
                { key: "all", label: "Everyone" },
                { key: "mine", label: "My program" },
              ]}
              value={scope}
              onChange={setScope}
            />
            {years.length > 0 && (
              <select className="select" value={year} onChange={(e) => setYear(Number(e.target.value))}>
                {years.map((y) => (
                  <option key={y} value={y}>
                    {y} portal
                  </option>
                ))}
              </select>
            )}
          </div>
        }
      />
      {!log.length ? (
        <Card>
          <Empty>The transfer portal opens after the first season.</Empty>
        </Card>
      ) : (
        <Card flush>
          <Table cols={cols} rows={rows} rowKey={(m) => m.pid} initialSort="ovr" limit={60} rowClass={(m) => (m.to === L.userTid || m.from === L.userTid ? "hl" : undefined)} />
        </Card>
      )}
    </div>
  );
}
