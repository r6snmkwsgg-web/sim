import { Link } from "react-router-dom";
import type { Bracket, BracketGame, Game, League } from "../../engine/types";
import { teamMaybe } from "../../engine/core";
import { Logo } from "./common";
import { cls } from "../util";

function TeamLine({ L, tid, seed, score, win, done }: { L: League; tid: number | null; seed: number | null; score: number | null; win: boolean; done: boolean }) {
  const t = teamMaybe(L, tid);
  return (
    <div className={cls("b-team", done && win && "win", done && !win && "lose", tid === L.userTid && "user")}>
      <span className="seed">{seed ?? ""}</span>
      {t ? <Logo team={t} size={18} /> : <span style={{ width: 18 }} />}
      <span className="nm">{t ? t.name : <span className="faint">TBD</span>}</span>
      <span className="sc">{score ?? ""}</span>
    </div>
  );
}

export function GameBox({ L, g, games }: { L: League; g: BracketGame; games: Map<number, Game> }) {
  const game = g.gid !== null ? games.get(g.gid) : undefined;
  const done = g.winner !== null && !!game?.played;
  const sa = game ? (game.home === g.a ? game.hs : game.as) : null;
  const sb = game ? (game.home === g.b ? game.hs : game.as) : null;
  const bye = g.a !== null && g.b === null && g.winner !== null;
  return (
    <div className="b-game">
      <TeamLine L={L} tid={g.a} seed={g.sa} score={done ? sa : null} win={g.winner === g.a} done={done} />
      {bye ? (
        <div className="b-team faint small" style={{ paddingLeft: 30 }}>
          bye
        </div>
      ) : (
        <TeamLine L={L} tid={g.b} seed={g.sb} score={done ? sb : null} win={g.winner === g.b} done={done} />
      )}
      {game && <Link className="box" to={`/l/${L.id}/game/${game.id}`} aria-label="Box score" />}
    </div>
  );
}

export function BracketView({ L, br, games, rounds, filter }: { L: League; br: Bracket; games: Map<number, Game>; rounds?: number[]; filter?: (g: BracketGame) => boolean }) {
  const maxRound = Math.max(...br.games.map((g) => g.round));
  const rs = rounds ?? Array.from({ length: maxRound + 1 }, (_, i) => i);
  return (
    <div className="bracket">
      {rs.map((r) => {
        const gs = br.games.filter((g) => g.round === r && (!filter || filter(g))).sort((a, b) => a.slot - b.slot);
        return (
          <div key={r} className="b-round">
            <div className="b-round-h">{r < 0 ? br.playinName : br.rounds[r]}</div>
            <div className="b-col">
              {gs.map((g) => (
                <GameBox key={`${g.round}-${g.slot}`} L={L} g={g} games={games} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
