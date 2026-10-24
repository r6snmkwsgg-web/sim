import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { Icon } from "../components/Icons";
import { team } from "../../engine/core";
import type { Bracket, Game } from "../../engine/types";
import { Card, Empty, Logo, PageHead, SeasonSelect, Seg, heroStyle } from "../components/common";
import { BracketView, GameBox } from "../components/Bracket";
import { fetchSeason, useAsync } from "../util";
import { REGION_NAMES } from "../../engine/postseason";

export function Tournaments() {
  const L = useLeague();
  const [sp, setSp] = useSearchParams();
  const season = Number(sp.get("season") ?? L.season);
  const { data, loading } = useAsync(async () => {
    if (season === L.season) return { brackets: L.brackets, games: L.games };
    const a = await fetchSeason(L, season);
    return { brackets: a?.brackets ?? [], games: a?.games ?? [] };
  }, [season, L.season, L.brackets, L.games.length, L.day]);
  const brackets = data?.brackets ?? [];
  const games = useMemo(() => new Map<number, Game>((data?.games ?? []).map((g) => [g.id, g])), [data]);
  const hasNational = brackets.some((b) => b.key === "ncaa");
  // follow the national bracket by default once it exists
  const [kind, setKind] = useState<string | null>(null);
  const want = kind ?? (hasNational ? "ncaa" : "conf");
  const k = want !== "conf" && !brackets.some((b) => b.key === want) ? "conf" : want;
  const ut = team(L, L.userTid);
  const [conf, setConf] = useState<number>(ut.cid);
  const [region, setRegion] = useState<number>(-1);
  const br: Bracket | undefined = k === "conf" ? brackets.find((b) => b.key === `conf:${conf}`) : brackets.find((b) => b.key === k);
  const userRegion = br?.key === "ncaa" ? br.games.find((g) => g.round === 0 && (g.a === L.userTid || g.b === L.userTid))?.region : undefined;
  const reg = region === -1 ? userRegion ?? 0 : region;
  return (
    <div>
      <PageHead
        title="Tournaments"
        sub={br ? `${br.name}${br.champion !== null ? ` · Champion: ${team(L, br.champion).name}` : ""}` : ""}
        right={
          <div className="row">
            <Seg
              options={[
                { key: "conf", label: "Conference" },
                { key: "ncaa", label: "NCAA" },
                { key: "nit", label: "NIT" },
                { key: "cbi", label: "CBI" },
              ]}
              value={k}
              onChange={setKind}
            />
            {k === "conf" && (
              <select className="select" value={conf} onChange={(e) => setConf(Number(e.target.value))}>
                {L.conferences.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            )}
            <SeasonSelect L={L} value={season} onChange={(s) => setSp({ season: String(s) })} />
          </div>
        }
      />
      {loading && !data ? (
        <Empty>Loading…</Empty>
      ) : !br ? (
        <Card>
          <Empty>{k === "conf" ? "Conference tournaments begin after the regular season." : "The national postseason brackets are announced on Selection Sunday."}</Empty>
        </Card>
      ) : br.key === "ncaa" ? (
        <div className="col gap-16">
          {br.champion !== null && (
            <div className="hero-banner" style={heroStyle(team(L, br.champion).colors)}>
              <div className="hero-inner" style={{ padding: "18px 24px" }}>
                <span className="trophy-big" style={{ width: 62, height: 62 }}>
                  <Icon name="awards" size={32} />
                </span>
                <Logo team={team(L, br.champion)} size={64} />
                <div>
                  <div className="hero-kicker">National champion</div>
                  <div className="hero-title" style={{ fontSize: 34, marginTop: 4 }}>
                    <Link to={`/l/${L.id}/team/${br.champion}?season=${season}`}>
                      {team(L, br.champion).name} {team(L, br.champion).mascot}
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div className="row">
            <Seg
              options={[...REGION_NAMES.map((n, i) => ({ key: i, label: `${n}` })), { key: 4, label: "Final Four" }]}
              value={reg}
              onChange={setRegion}
            />
          </div>
          {reg < 4 ? (
            <div className="card card-b">
              <BracketView L={L} br={br} games={games} rounds={[0, 1, 2, 3]} filter={(g) => g.region === reg} />
            </div>
          ) : (
            <div className="card card-b">
              <BracketView L={L} br={br} games={games} rounds={[4, 5]} />
            </div>
          )}
          {br.games.some((g) => g.round < 0) && (
            <Card title={br.playinName ?? "First Four"}>
              <div className="row-wrap" style={{ alignItems: "flex-start" }}>
                {br.games
                  .filter((g) => g.round < 0)
                  .map((g) => (
                    <div key={g.slot} style={{ width: 230 }}>
                      <div className="tiny muted" style={{ marginLeft: 12 }}>
                        {REGION_NAMES[g.region ?? 0]} · {g.sa} seed
                      </div>
                      <GameBox L={L} g={g} games={games} />
                    </div>
                  ))}
              </div>
            </Card>
          )}
        </div>
      ) : (
        <div className="card card-b">
          <BracketView L={L} br={br} games={games} />
        </div>
      )}
    </div>
  );
}
