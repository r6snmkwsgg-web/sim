// ==UserScript==
// @name         WAS Dynasty: in-season progs
// @namespace    was-dynasty-fbgm
// @version      1.0
// @description  Turns on the 30% offseason / 70% in-season progression every time Football GM opens. Only acts in the WAS Dynasty league.
// @match        https://play.football-gm.com/*
// @grant        none
// @inject-into  page
// @sandbox      raw
// @run-at       document-idle
// ==/UserScript==

async function pgmInSeasonProgs() {
	// PGM-style in-season progression for the WAS Dynasty league in Football GM.
	// When the new season's progs land in the preseason, every player keeps 30% of his change right away. The other
	// 70% arrives in 4 equal steps after your team's games 4, 8, 12 and 16 (anything left lands when the playoffs
	// start). End-of-season ratings come out exactly as Football GM rolled them; only the timing changes.
	// Each step is saved on the player, so loading this again never applies anything twice.
	// It only acts in the WAS Dynasty league (checks that player 5263 is Jason Latham); other leagues are left alone.
	if (self.__pgmProg) clearInterval(self.__pgmProg);
	self.__pgmProgKey = "";
	const KEYS = ["hgt", "stre", "spd", "endu", "thv", "thp", "tha", "bsc", "elu", "rtr", "hnd", "rbk", "pbk", "pcv", "tck", "prs", "rns", "kpw", "kac", "ppw", "pac"];
	const NOW = 0.3;
	const STEPS = [4, 8, 12, 16];
	const { PHASE, PLAYER, idb, g, player, lock, helpers } = bbgm;

	const isWasLeague = async () => {
		const lid = g.lid;
		if (lid === undefined) return false;
		if (self.__pgmProgLid === lid) return self.__pgmProgIsWas;
		const p = await idb.getCopy.players({ pid: 5263 }, "noCopyCache");
		if (!p) return false; // league still loading, check again next time
		self.__pgmProgLid = lid;
		self.__pgmProgIsWas = p.firstName === "Jason" && p.lastName === "Latham";
		return self.__pgmProgIsWas;
	};
	const save = async (p) => {
		await player.develop(p, 0);
		player.updateValues(p);
		await idb.cache.players.put(p);
	};
	const part = (total, k) => Math.round((total * k) / STEPS.length) - Math.round((total * (k - 1)) / STEPS.length);
	const addStash = (p, rows, from, to) => {
		// add steps from+1..to of the stash to the given ratings rows
		for (const key of Object.keys(p.pgmProg.stash)) {
			let amt = 0;
			for (let k = from + 1; k <= to; k++) amt += part(p.pgmProg.stash[key], k);
			if (amt !== 0) for (const r of rows) r[key] = helpers.bound(r[key] + amt, 0, 100);
		}
	};
	const userGp = async (season) => {
		const ts = await idb.cache.teamSeasons.indexGet("teamSeasonsByTidSeason", [g.get("userTid"), season]);
		return ts ? helpers.getTeamSeasonGp(ts) : 0;
	};

	const run = async () => {
		if (g.lid === undefined || lock.get("newPhase")) return null;
		if (!(await isWasLeague())) return null;
		const season = g.get("season");
		const phase = g.get("phase");
		const gp = phase === PHASE.REGULAR_SEASON || phase === PHASE.AFTER_TRADE_DEADLINE ? await userGp(season) : 0;
		const key = `${g.lid}-${season}-${phase}-${gp}`;
		if (key === self.__pgmProgKey) return null;
		const inSeason = phase >= PHASE.PRESEASON && phase <= PHASE.AFTER_TRADE_DEADLINE;
		const canSplit = phase === PHASE.PRESEASON || (phase === PHASE.REGULAR_SEASON && gp === 0);
		const stepsDue = phase >= PHASE.PLAYOFFS ? STEPS.length : STEPS.filter((x) => gp >= x).length;
		const out = { split: 0, stepped: 0, flushed: 0 };
		const ps = await idb.cache.players.indexGetAll("playersByTid", [PLAYER.FREE_AGENT, Infinity]);
		for (const p of ps) {
			const prog = p.pgmProg;
			// leftovers from an older season (script wasn't running at the end of it): land them now
			if (prog && prog.season < season && prog.done < STEPS.length) {
				addStash(p, p.ratings.filter((r) => r.season >= prog.season), prog.done, STEPS.length);
				prog.done = STEPS.length;
				await save(p);
				out.flushed += 1;
			}
			// new season's progs: keep 30% now, hold back 70%
			if (canSplit && (!p.pgmProg || p.pgmProg.season < season)) {
				const cur = p.ratings.filter((r) => r.season === season);
				const prev = p.ratings.filter((r) => r.season === season - 1).at(-1);
				const stash = {};
				if (cur.length > 0 && prev) {
					const last = cur.at(-1);
					for (const k of KEYS) {
						if (typeof last[k] !== "number" || typeof prev[k] !== "number") continue;
						const d = last[k] - prev[k];
						const hold = d - Math.round(d * NOW);
						if (hold !== 0) stash[k] = hold;
					}
					for (const k of Object.keys(stash)) for (const r of cur) r[k] -= stash[k];
				}
				p.pgmProg = { season, stash, done: Object.keys(stash).length > 0 ? 0 : STEPS.length };
				if (Object.keys(stash).length > 0) {
					await save(p);
					out.split += 1;
				} else {
					await idb.cache.players.put(p);
				}
				continue;
			}
			// in-season steps
			if (p.pgmProg && p.pgmProg.season === season && p.pgmProg.done < stepsDue && (inSeason || phase >= PHASE.PLAYOFFS)) {
				addStash(p, [p.ratings.at(-1)], p.pgmProg.done, stepsDue);
				p.pgmProg.done = stepsDue;
				await save(p);
				out.stepped += 1;
			}
		}
		self.__pgmProgKey = key;
		return { season, phase, gp, stepsDue, ...out };
	};

	const guarded = async () => {
		if (self.__pgmProgBusy) return null;
		self.__pgmProgBusy = true;
		try {
			return await run();
		} catch (e) {
			console.log("PGM progression error: " + e.message);
			return null;
		} finally {
			self.__pgmProgBusy = false;
		}
	};
	self.__pgmProg = setInterval(guarded, 2000);

	// status line
	const first = await guarded();
	if (g.lid === undefined) {
		console.log("PGM in-season progression is ON. It kicks in when you open the WAS Dynasty league.");
		return;
	}
	if (!(await isWasLeague())) {
		console.log("PGM in-season progression is ON, but this isn't the WAS Dynasty league, so it does nothing here.");
		return;
	}
	const all = await idb.cache.players.indexGetAll("playersByTid", [PLAYER.FREE_AGENT, Infinity]);
	const season = g.get("season");
	const mine = all.filter((p) => p.pgmProg && p.pgmProg.season === season && Object.keys(p.pgmProg.stash).length > 0);
	const pending = mine.filter((p) => p.pgmProg.done < STEPS.length).length;
	let status;
	if (mine.length === 0) {
		status = g.get("phase") < PHASE.PRESEASON || g.get("phase") > PHASE.PLAYOFFS
			? `Waiting for the ${season + 1} preseason progs.`
			: `No split for ${season} (the season was already under way when this first ran). It starts next preseason.`;
	} else {
		const done = Math.min(...mine.map((p) => p.pgmProg.done));
		status = pending > 0
			? `${season}: 30% of progs applied, ${done} of 4 in-season steps done (next after your team's game ${STEPS[done]}).`
			: `${season}: all progs applied.`;
	}
	console.log(`PGM in-season progression is ON. ${status}` + (first && (first.split || first.stepped || first.flushed) ? ` Just now: split ${first.split}, stepped ${first.stepped}, caught up ${first.flushed}.` : ""));
}

(async () => {
	// wait for Football GM to start, then hand the progression code to its game engine
	for (let i = 0; i < 240 && !(window.bbgm && window.bbgm.toWorker); i++) {
		await new Promise((resolve) => setTimeout(resolve, 500));
	}
	if (!window.bbgm || !window.bbgm.toWorker) return;
	const out = await window.bbgm.toWorker("main", "evalOnWorker", `await (${pgmInSeasonProgs.toString()})();`);
	console.log(out);
})();
