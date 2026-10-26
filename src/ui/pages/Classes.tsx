import { useState } from "react";
import { useLeague } from "../store";
import { classRankings, classUnrated, commitsFor, RATINGS_DAY } from "../../engine/recruiting";
import { Card, Empty, PageHead, Seg, Stars, Table, TeamLink, type Col } from "../components/common";
import { shortDayLabel, team } from "../../engine/core";

type Row = ReturnType<typeof classRankings>[number];

export function ClassRankings() {
  const L = useLeague();
  const [kind, setKind] = useState<"hs" | "portal">("hs");
  const rows = classRankings(L, kind).filter((r) => r.n > 0);
  const cols: Col<Row>[] = [
    { key: "rank", label: "Rk", render: (r) => <b>{r.rank}</b>, sort: (r) => -r.rank, num: true },
    { key: "team", label: "Program", render: (r) => <TeamLink L={L} tid={r.tid} />, sort: (r) => team(L, r.tid).name },
    { key: "conf", label: "Conf", render: (r) => <span className="muted">{L.conferences[team(L, r.tid).cid].short}</span> },
    { key: "n", label: "Commits", render: (r) => r.n, sort: (r) => r.n, num: true },
    { key: "avg", label: "Avg", render: (r) => <Stars n={Math.round(r.avgStars * 2) / 2} />, sort: (r) => r.avgStars, num: true },
    {
      key: "list",
      label: "Players",
      render: (r) => (
        <span className="small muted">
          {commitsFor(L, r.tid)
            .filter((p) => p.recruit?.kind === kind)
            .sort((a, b) => b.recruit!.stars - a.recruit!.stars)
            .map((p) => `${p.recruit!.stars}★ ${p.pos}`)
            .join(" · ")}
        </span>
      ),
    },
    { key: "pts", label: "Points", render: (r) => r.pts, sort: (r) => r.pts, num: true },
  ];
  return (
    <div>
      <PageHead
        title="Class Rankings"
        sub="Points: 5★ 100 · 4★ 60 · 3★ 30 · 2★ 12 · 1★ 4"
        right={
          <Seg
            options={[
              { key: "hs", label: "High school" },
              { key: "portal", label: "Transfer portal" },
            ]}
            value={kind}
            onChange={setKind}
          />
        }
      />
      {kind === "hs" && classUnrated(L) ? (
        <Card>
          <Empty>The class is unrated until the rankings come out on {shortDayLabel(L.season, RATINGS_DAY)}. Until then nobody knows whose class is best.</Empty>
        </Card>
      ) : (
        <Card flush>
          <Table cols={cols} rows={rows} rowKey={(r) => r.tid} initialSort="pts" limit={50} rowClass={(r) => (r.tid === L.userTid ? "hl" : undefined)} empty="No commitments yet." />
        </Card>
      )}
    </div>
  );
}
