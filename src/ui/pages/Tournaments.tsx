import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { Icon } from "../components/Icons";
import { CT_START, SELECTION_DAY, shortDayLabel, team, teamMaybe } from "../../engine/core";
import type { Bracket, BracketGame, Game, League } from "../../engine/types";
import { Card, Empty, Logo, PageHead, SeasonSelect, Seg, heroStyle } from "../components/common";
import { BracketView, GameBox } from "../components/Bracket";
import { fetchSeason, useAsync } from "../util";
import { confStandings, isEvent, REGION_NAMES } from "../../engine/postseason";
import { thanksgivingDay } from "../../engine/events";

/** The brackets and games of the season picked in the URL (this season by default). */
function useSeasonBrackets() {
  const L = useLeague();
  const [sp, setSp] = useSearchParams();
  const season = Number(sp.get("season") ?? L.season);
  const { data, loading } = useAsync(async () => {
    if (season === L.season) return { brackets: L.brackets, games: L.games };
    const a = await fetchSeason(L, season);
    return { brackets: a?.brackets ?? [], games: a?.games ?? [] };
  }, [season, L.season, L.brackets, L.games.length, L.day]);
  const games = useMemo(() => new Map<number, Game>((data?.games ?? []).map((g) => [g.id, g])), [data]);
  const picker = <SeasonSelect L={L} value={season} onChange={(s) => setSp({ season: String(s) })} />;
  return { L, season, brackets: data?.brackets ?? [], games, loading: loading && !data, picker };
}

function ChampionBanner({ L, tid, season, kicker }: { L: League; tid: number; season: number; kicker: string }) {
  const t = team(L, tid);
  return (
    <div className="hero-banner" style={heroStyle(t.colors)}>
      <div className="hero-inner" style={{ padding: "18px 24px" }}>
        <span className="trophy-big" style={{ width: 62, height: 62 }}>
          <Icon name="awards" size={32} />
        </span>
        <Logo team={t} size={64} />
        <div>
          <div className="hero-kicker">{kicker}</div>
          <div className="hero-title" style={{ fontSize: 34, marginTop: 4 }}>
            <Link to={`/l/${L.id}/team/${tid}?season=${season}`}>
              {t.name} {t.mascot}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------- NCAA Tournament ----------------
export function Tournaments() {
  const { L, season, brackets, games, loading, picker } = useSeasonBrackets();
  const br = brackets.find((b) => b.key === "ncaa");
  const [region, setRegion] = useState<number>(-1);
  const userRegion = br?.games.find((g) => g.round === 0 && (g.a === L.userTid || g.b === L.userTid))?.region;
  const reg = region === -1 ? userRegion ?? 0 : region;
  return (
    <div className="col gap-16">
      <PageHead title="NCAA Tournament" sub={br ? `${br.name}${br.champion !== null ? ` · Champion: ${team(L, br.champion).name}` : ""}` : "The field of 68"} right={picker} />
      {loading ? (
        <Empty>Loading…</Empty>
      ) : !br ? (
        <Card>
          <Empty>
            {season === L.season ? `The field of 68 is announced on Selection Sunday, ${shortDayLabel(L.season, SELECTION_DAY)}.` : "No NCAA Tournament was recorded for this season."}
          </Empty>
        </Card>
      ) : (
        <>
          {br.champion !== null && <ChampionBanner L={L} tid={br.champion} season={season} kicker="National champion" />}
          <div className="row">
            <Seg options={[...REGION_NAMES.map((n, i) => ({ key: i, label: `${n}` })), { key: 4, label: "Final Four" }]} value={reg} onChange={setRegion} />
          </div>
          <div className="card card-b">
            {reg < 4 ? <BracketView L={L} br={br} games={games} rounds={[0, 1, 2, 3]} filter={(g) => g.region === reg} /> : <BracketView L={L} br={br} games={games} rounds={[4, 5]} />}
          </div>
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
        </>
      )}
    </div>
  );
}

// ---------------- Conference tournaments ----------------
function bracketStatus(L: League, br: Bracket): string {
  if (br.champion !== null) return "Final";
  const live = br.games.filter((g) => g.winner === null && g.a !== null && g.b !== null).sort((a, b) => a.round - b.round)[0];
  return live ? br.rounds[live.round] ?? "In progress" : "In progress";
}

export function ConfTourneys() {
  const { L, season, brackets, games, loading, picker } = useSeasonBrackets();
  const ut = team(L, L.userTid);
  const [pick, setPick] = useState<number>(ut.cid);
  const confs = brackets.filter((b) => b.key.startsWith("conf:"));
  const current = season === L.season;
  const decided = confs.filter((b) => b.champion !== null).length;
  const br = confs.find((b) => b.key === `conf:${pick}`);
  const conf = L.conferences.find((c) => c.id === pick);
  const order = L.conferences.slice().sort((a, b) => (a.id === ut.cid ? -1 : b.id === ut.cid ? 1 : a.name.localeCompare(b.name)));
  return (
    <div className="col gap-16">
      <PageHead
        title="Conference Tournaments"
        sub={confs.length ? `${decided} of ${confs.length} decided. Every champion earns an automatic NCAA bid.` : current ? `They start ${shortDayLabel(L.season, CT_START)}, right after the regular season. Every champion earns an automatic NCAA bid.` : "Every champion earns an automatic NCAA bid."}
        right={picker}
      />
      {loading ? (
        <Empty>Loading…</Empty>
      ) : (
        <div className="grid g-main" style={{ alignItems: "start" }}>
          <Card title={conf ? `${conf.name} Tournament` : "Bracket"} sub={br ? (br.champion !== null ? `Champion: ${team(L, br.champion).name}` : bracketStatus(L, br)) : undefined}>
            {br ? (
              <BracketView L={L} br={br} games={games} />
            ) : (
              <Empty>{current ? "Brackets are set when the regular season ends. Seeds follow the final conference standings." : "No bracket was recorded for this conference this season."}</Empty>
            )}
          </Card>
          <Card title="All conferences" flush>
            <table className="tbl compact">
              <tbody>
                {order.map((c) => {
                  const b = confs.find((x) => x.key === `conf:${c.id}`);
                  const leader = !b && current ? confStandings(L, c.id)[0] : undefined;
                  const champ = b?.champion ?? null;
                  return (
                    <tr key={c.id} className={`clickable${c.id === pick ? " sel" : ""}`} onClick={() => setPick(c.id)}>
                      <td>
                        <b>{c.short}</b>
                        {c.id === ut.cid && <span className="badge" style={{ marginLeft: 6 }}>Yours</span>}
                      </td>
                      <td>
                        {champ !== null ? (
                          <span className="row" style={{ gap: 6 }}>
                            <Logo team={team(L, champ)} size={18} /> {team(L, champ).name}
                            <Icon name="awards" size={13} />
                          </span>
                        ) : b ? (
                          <span className="muted">{bracketStatus(L, b)}</span>
                        ) : leader !== undefined ? (
                          <span className="row muted" style={{ gap: 6 }}>
                            <Logo team={team(L, leader)} size={18} /> {team(L, leader).name} leads
                          </span>
                        ) : (
                          <span className="muted">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </Card>
        </div>
      )}
    </div>
  );
}

// ---------------- NIT & CBI ----------------
export function NitCbi() {
  const { L, season, brackets, games, loading, picker } = useSeasonBrackets();
  const [kind, setKind] = useState<"nit" | "cbi">("nit");
  const br = brackets.find((b) => b.key === kind);
  return (
    <div className="col gap-16">
      <PageHead title="NIT & CBI" sub="The postseason for teams that miss the NCAA field." right={picker} />
      <div className="row">
        <Seg
          options={[
            { key: "nit", label: "NIT" },
            { key: "cbi", label: "CBI" },
          ]}
          value={kind}
          onChange={setKind}
        />
      </div>
      {loading ? (
        <Empty>Loading…</Empty>
      ) : !br ? (
        <Card>
          <Empty>{season === L.season ? `The ${kind.toUpperCase()} field is announced on Selection Sunday, ${shortDayLabel(L.season, SELECTION_DAY)}.` : `No ${kind.toUpperCase()} was recorded for this season.`}</Empty>
        </Card>
      ) : (
        <>
          {br.champion !== null && <ChampionBanner L={L} tid={br.champion} season={season} kicker={`${br.name} champion`} />}
          <div className="card card-b">
            <BracketView L={L} br={br} games={games} />
          </div>
        </>
      )}
    </div>
  );
}

// ---------------- Early-season events ----------------
function fieldOf(br: Bracket): number[] {
  return br.games.filter((g) => g.round === 0).flatMap((g) => [g.a, g.b]).filter((t): t is number => t !== null);
}

/** Final places from the placement games (1st, 2nd, ...) once they're played. */
function placesOf(br: Bracket): Map<number, number> {
  const out = new Map<number, number>();
  for (const g of br.games) {
    if (g.place === undefined || g.winner === null) continue;
    out.set(g.winner, g.place);
    const l = g.winner === g.a ? g.b : g.a;
    if (l !== null) out.set(l, g.place + 1);
  }
  return out;
}

function eventDates(L: League, season: number, br: Bracket): string {
  return `${shortDayLabel(season, br.days[0])} to ${shortDayLabel(season, br.days[br.days.length - 1])}`;
}

function EventDetail({ L, br, games, season }: { L: League; br: Bracket; games: Map<number, Game>; season: number }) {
  const extra = br.games.filter((g) => g.slot >= 10).sort((a, b) => a.round - b.round || a.slot - b.slot);
  const places = placesOf(br);
  const field = fieldOf(br).sort((a, b) => (places.get(a) ?? 99) - (places.get(b) ?? 99));
  const label = (g: BracketGame) => g.label ?? br.rounds[g.round];
  return (
    <Card title={br.name} sub={`${eventDates(L, season, br)} · ${field.length} teams, neutral site${br.champion !== null ? ` · Champion: ${team(L, br.champion).name}` : ""}`}>
      <div className="col gap-16">
        <BracketView L={L} br={br} games={games} filter={(g) => g.slot < 10} />
        {extra.length > 0 && (
          <div>
            <div className="section-title">Consolation and placement games</div>
            <div className="row-wrap" style={{ alignItems: "flex-start" }}>
              {extra.map((g) => (
                <div key={`${g.round}-${g.slot}`} style={{ width: 230 }}>
                  <div className="tiny muted" style={{ marginLeft: 12 }}>
                    {label(g)}
                  </div>
                  <GameBox L={L} g={g} games={games} />
                </div>
              ))}
            </div>
          </div>
        )}
        {places.size > 0 && (
          <div>
            <div className="section-title">Final standings</div>
            <div className="event-places">
              {field.map((tid) => (
                <Link key={tid} to={`/l/${L.id}/team/${tid}?season=${season}`} className={`event-place${tid === L.userTid ? " me" : ""}`}>
                  <b>{places.get(tid) ?? "-"}</b>
                  <Logo team={team(L, tid)} size={20} />
                  <span className="ellipsis">{team(L, tid).name}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

export function EarlyEvents() {
  const { L, season, brackets, games, loading, picker } = useSeasonBrackets();
  const events = brackets.filter(isEvent);
  const mine = events.find((b) => fieldOf(b).includes(L.userTid));
  const [pick, setPick] = useState<string | null>(null);
  const sel = events.find((b) => b.key === pick) ?? mine ?? events[0];
  const T = thanksgivingDay(season);
  return (
    <div className="col gap-16">
      <PageHead
        title="Early-Season Events"
        sub={`Thanksgiving week, ${shortDayLabel(season, T - 3)} to ${shortDayLabel(season, T + 2)}. Eight-team events play three days with consolation games; four-team events play two. They count as nonconference games.`}
        right={picker}
      />
      {loading ? (
        <Empty>Loading…</Empty>
      ) : !events.length ? (
        <Card>
          <Empty>No early-season events were recorded for this season.</Empty>
        </Card>
      ) : (
        <>
          {sel && <EventDetail L={L} br={sel} games={games} season={season} />}
          <div className="event-grid">
            {events.map((b) => {
              const field = fieldOf(b);
              const started = b.games.some((g) => g.winner !== null);
              return (
                <button key={b.key} className={`event-card${b === sel ? " on" : ""}`} onClick={() => setPick(b.key)}>
                  <div className="row" style={{ justifyContent: "space-between", gap: 8 }}>
                    <b className="ellipsis">{b.name}</b>
                    {field.includes(L.userTid) && <span className="badge gold">You</span>}
                  </div>
                  <div className="tiny muted">
                    {eventDates(L, season, b)} · {field.length} teams
                  </div>
                  <div className="event-logos">
                    {field.map((tid) => (
                      <Logo key={tid} team={teamMaybe(L, tid)} size={22} />
                    ))}
                  </div>
                  <div className="small">
                    {b.champion !== null ? (
                      <span className="row" style={{ gap: 6 }}>
                        <Icon name="awards" size={13} /> <b>{team(L, b.champion).name}</b>
                      </span>
                    ) : (
                      <span className="muted">{started ? "In progress" : `Tips off ${shortDayLabel(season, b.days[0])}`}</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
