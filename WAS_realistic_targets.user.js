// ==UserScript==
// @name         Football GM: Realistic Targets
// @namespace    was-dynasty-fbgm
// @version      1.0
// @description  Rewrites how quarterbacks pick receivers in Football GM, league-wide: a depth-chart pecking order, stars get fed, situational reads (deep shots, red zone, short yardage, 3rd & long), receiver-vs-coverage matchups, QB chemistry, a hot hand, and diminishing returns. If Football GM changes and the hook can't be found, the game runs with its normal targeting and a small notice says the mod is off.
// @match        https://play.football-gm.com/*
// @grant        none
// @inject-into  page
// @sandbox      raw
// @run-at       document-idle
// ==/UserScript==

// ============================================================================================================
// SETTINGS: change these numbers to tune the mod. Save, then close every Football GM tab and open it again.
// ============================================================================================================
const WAS_TARGET_SETTINGS = {
	enabled: true, // false = normal Football GM targeting

	// How much better receivers get fed. Each receiver is compared with the league average at his own position
	// (a WR with WRs, a TE with TEs...). 0 = talent doesn't matter, higher = stars soak up more targets.
	starPower: 2.0,

	// Pecking order: base target weight by depth chart slot (1st, 2nd, 3rd... at that position).
	pecking: {
		enabled: true,
		WR: [1.0, 0.75, 0.55, 0.22, 0.18],
		TE: [0.7, 0.3, 0.25],
		RB: [0.55, 0.3, 0.25],
	},

	// No single receiver gets more than this share of the looks on any one throw.
	maxShare: 0.4,

	// Down, distance and field position.
	situational: {
		enabled: true,
		deepChance: 0.15, // share of normal throws where the QB looks deep (speed matters)
		deepChanceLong: 0.32, // same, on 3rd/4th & 8+
		deepSpeedPower: 3, // how much speed matters on a deep look
		deepRB: 0.35, // RBs on a deep look
		redZoneHeight: 0.5, // inside the 20: bonus for tall targets
		redZoneTE: 1.25, // inside the 20: tight ends
		shortYardageTERB: 1.3, // 3 yards or less to go: TEs and RBs
		goToGuy: 1.1, // 3rd/4th & 8+: WR1 is the go-to guy
	},

	// Receiver vs his defender: WR1 vs the top corner, WR2 vs CB2..., TE vs safety/LB, RB vs LB.
	matchups: { enabled: true, power: 1.5, min: 0.6, max: 1.6 },

	// QB chemistry: guys who have produced this season (yards per target vs league average) get looked at more.
	chemistry: { enabled: true, weight: 0.5, cap: 0.3, minTargets: 15 },

	// Hot hand: each catch this game makes the QB a bit more likely to come back to him.
	hotHand: { enabled: true, perCatch: 0.03, maxCatches: 6 },

	// Diminishing returns: after this many targets in a game, each extra one gets less likely.
	diminishing: { enabled: true, softCap: 8, rate: 0.15 },
};

// ============================================================================================================
// Runs inside Football GM's game engine (handed over with evalOnWorker). Wraps GameSim.pickPlayer: the call that
// picks a pass target (WR/TE/RB, getting open or catching, power 1.5) goes through the new logic; every other call
// (tacklers, pass rushers, defenders, returners...) is untouched. Re-running it just swaps in new settings.
// ============================================================================================================
function wasTargetModInstall(cfg) {
	const VERSION = "1.0";
	const bbgm = self.bbgm;
	const GS = bbgm && bbgm.GameSim;
	if (!GS || !GS.prototype || typeof GS.prototype.pickPlayer !== "function") {
		return { ok: false, reason: "Football GM's game engine changed (no GameSim.pickPlayer)." };
	}
	const proto = GS.prototype;
	const orig = proto.__wasTgtOrig || proto.pickPlayer;
	proto.__wasTgtOrig = orig;

	const st = self.__wasTargetMod || (self.__wasTargetMod = { routed: 0, errors: 0, lastError: null, chem: { at: 0, loading: false, map: new Map(), lgYpt: 0, hgt: new Map() } });
	st.avg = st.avg || {};
	st.avgN = st.avgN || {};
	st.cfg = cfg;
	st.version = VERSION;

	const fat = (energy, injured) => (injured ? 0 : Math.min(1, energy + 0.05));
	const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

	// Season production + heights, refreshed in the background (target picks can't wait on the database).
	const refreshChem = async () => {
		const c = st.chem;
		if (c.loading || Date.now() - c.at < 15000) return;
		c.loading = true;
		try {
			const season = bbgm.g.get("season");
			const ps = await bbgm.idb.cache.players.getAll();
			const map = new Map();
			const h = new Map();
			let tgt = 0;
			let yds = 0;
			for (const p of ps) {
				const r = p.ratings && p.ratings[p.ratings.length - 1];
				if (r) h.set(p.pid, r.hgt);
				const m = { tgt: 0, rec: 0, yds: 0 };
				for (const row of p.stats || []) {
					if (row.season !== season || row.playoffs) continue;
					m.tgt += row.tgt || 0;
					m.rec += row.rec || 0;
					m.yds += row.recYds || 0;
				}
				if (m.tgt > 0) {
					map.set(p.pid, m);
					tgt += m.tgt;
					yds += m.yds;
				}
			}
			c.map = map;
			c.hgt = h;
			c.lgYpt = tgt > 200 ? yds / tgt : 0;
			c.at = Date.now();
		} catch (e) {
			st.lastError = "chemistry: " + (e && e.message);
		} finally {
			c.loading = false;
		}
	};

	const pickTarget = (gs, t, rating) => {
		const C = st.cfg;
		const pof = gs.playersOnField[t] || {};
		const cands = [];
		for (const pos of ["WR", "TE", "RB"]) {
			for (const p of pof[pos] || []) cands.push({ p, pos });
		}
		if (cands.length === 0) return null;

		const dTeam = gs.playersOnField[t === gs.o ? gs.d : gs.o] || {};
		const depth = (gs.team[t] && gs.team[t].depth) || {};
		const rankOf = (pos, p) => {
			let i = 0;
			for (const x of depth[pos] || []) {
				if (x === p) return i;
				if (!x.injured) i += 1;
			}
			return 9;
		};

		const down = gs.down;
		const toGo = gs.toGo;
		const scr = gs.scrimmage; // yards from own goal line
		const S = C.situational;
		const sit = S && S.enabled;
		const redZone = sit && scr >= 80;
		const longDown = sit && down >= 3 && toGo >= 8;
		const shortYd = sit && toGo <= 3;
		let deepChance = sit ? (longDown ? S.deepChanceLong : S.deepChance) : 0;
		if (redZone || 100 - scr < 25) deepChance = 0;
		const deep = deepChance > 0 && Math.random() < deepChance;

		if ((C.chemistry && C.chemistry.enabled) || sit) refreshChem();
		const chem = st.chem;

		// coverage players, best first (playersOnField keeps depth order)
		const cov = (p) => (p ? p.compositeRating.passCoverage * fat(p.stat.energy, p.injured) : 0);
		const CB = dTeam.CB || [];
		const SS = dTeam.S || [];
		const LB = dTeam.LB || [];
		// WR n is covered by CB n (then safeties, then a linebacker); RBs by the top linebacker
		const defFor = (pos, rank) => (pos === "WR" ? CB[rank] || SS[rank - CB.length] || LB[0] : LB[0] || SS[0]);

		for (const c of cands) {
			const p = c.p;
			const f = fat(p.stat.energy, p.injured);
			const raw = p.compositeRating[rating] || 0;
			const q = raw * f;
			c.rank = rankOf(c.pos, p);
			c.open = (p.compositeRating.gettingOpen || 0) * f;

			// league average at his position, learned as games are played
			const key = c.pos + ":" + rating;
			const prev = st.avg[key];
			const avg = prev === undefined ? raw || 0.5 : prev;
			if (raw > 0) {
				const n = (st.avgN[key] = (st.avgN[key] || 0) + 1);
				const a = Math.max(1 / n, 0.001);
				st.avg[key] = prev === undefined ? raw : prev * (1 - a) + raw * a;
			}
			let w = q > 0 && avg > 0 ? (q / avg) ** (C.starPower ?? 1.5) : 0;

			if (C.pecking && C.pecking.enabled) {
				const arr = C.pecking[c.pos] || [1];
				w *= arr[Math.min(c.rank, arr.length - 1)];
			}

			if (sit) {
				if (deep) {
					w *= ((p.compositeRating.speed || 0.5) / 0.6) ** S.deepSpeedPower;
					if (c.pos === "RB") w *= S.deepRB;
				}
				if (redZone) {
					const h = chem.hgt.get(p.id);
					if (h !== undefined) w *= Math.max(0.5, 1 + (S.redZoneHeight * (h - 50)) / 50);
					if (c.pos === "TE") w *= S.redZoneTE;
				}
				if (shortYd && (c.pos === "TE" || c.pos === "RB")) w *= S.shortYardageTERB;
				if (longDown && c.pos === "WR" && c.rank === 0) w *= S.goToGuy;
			}

			if (C.chemistry && C.chemistry.enabled && chem.lgYpt > 0) {
				const m = chem.map.get(p.id);
				if (m && m.tgt >= C.chemistry.minTargets) {
					w *= 1 + C.chemistry.weight * clamp(m.yds / m.tgt / chem.lgYpt - 1, -C.chemistry.cap, C.chemistry.cap);
				}
			}

			if (C.hotHand && C.hotHand.enabled) {
				w *= 1 + C.hotHand.perCatch * Math.min(p.stat.rec || 0, C.hotHand.maxCatches);
			}

			if (C.diminishing && C.diminishing.enabled) {
				const n = p.stat.tgt || 0;
				if (n > C.diminishing.softCap) w *= Math.exp(-C.diminishing.rate * (n - C.diminishing.softCap));
			}
			c.w = w;
		}

		// matchups: who is winning his matchup, relative to his teammates on this play
		if (C.matchups && C.matchups.enabled) {
			const ratios = [];
			for (const c of cands) {
				let dc;
				if (c.pos === "TE") {
					const a = cov(SS[0]);
					const b = cov(LB[0]);
					dc = a && b ? (a + b) / 2 : a || b;
				} else {
					dc = cov(defFor(c.pos, c.rank));
				}
				c.ratio = dc > 0 && c.open > 0 ? c.open / dc : 0;
				if (c.ratio > 0) ratios.push(c.ratio);
			}
			if (ratios.length) {
				const mean = ratios.reduce((a, b) => a + b, 0) / ratios.length;
				for (const c of cands) {
					if (c.ratio > 0) c.w *= clamp((c.ratio / mean) ** C.matchups.power, C.matchups.min, C.matchups.max);
				}
			}
		}

		let tot = 0;
		for (const c of cands) tot += c.w > 0 ? c.w : 0;
		if (!(tot > 0)) return null;

		// nobody gets more than maxShare of the looks on one throw
		const cap = C.maxShare;
		if (cap > 0 && cap < 1 && cands.length > 1) {
			for (const c of cands) {
				if (c.w > 0 && c.w / tot > cap) {
					const rest = tot - c.w;
					if (rest > 0) {
						c.w = (cap / (1 - cap)) * rest;
						tot = rest + c.w;
					}
				}
			}
		}
		let r = Math.random() * tot;
		for (const c of cands) {
			if (!(c.w > 0)) continue;
			r -= c.w;
			if (r <= 0) return c.p;
		}
		return cands[cands.length - 1].p;
	};

	proto.pickPlayer = function (t, rating, positions, power) {
		const C = st.cfg;
		if (
			C &&
			C.enabled &&
			power === 1.5 &&
			(rating === "gettingOpen" || rating === "catching") &&
			positions &&
			positions.length === 3 &&
			positions[0] === "WR" &&
			positions[1] === "TE" &&
			positions[2] === "RB"
		) {
			try {
				const p = pickTarget(this, t, rating);
				if (p) {
					st.routed += 1;
					return p;
				}
			} catch (e) {
				st.errors += 1;
				st.lastError = String((e && e.stack) || e).slice(0, 300);
			}
		}
		return orig.call(this, t, rating, positions, power);
	};
	return { ok: true, version: VERSION, routed: st.routed, errors: st.errors };
}

(async () => {
	"use strict";
	// wait for Football GM to start
	for (let i = 0; i < 240 && !(window.bbgm && window.bbgm.toWorker); i++) {
		await new Promise((resolve) => setTimeout(resolve, 500));
	}

	const badge = (text, ok) => {
		const show = () => {
			let el = document.getElementById("was-target-mod-badge");
			if (!el) {
				el = document.createElement("div");
				el.id = "was-target-mod-badge";
				el.style.cssText =
					"position:fixed;left:10px;bottom:40px;z-index:2000;padding:4px 10px;border-radius:12px;font:600 12px system-ui,sans-serif;box-shadow:0 1px 4px rgba(0,0,0,.3);cursor:pointer;transition:opacity .6s";
				el.title = "Football GM: Realistic Targets. Click to hide.";
				el.addEventListener("click", () => el.remove());
				document.body.appendChild(el);
			}
			el.textContent = text;
			el.style.background = ok ? "#1f6f43" : "#a33";
			el.style.color = "#fff";
			el.style.opacity = "1";
			if (ok) {
				setTimeout(() => {
					el.style.opacity = "0";
					setTimeout(() => el.remove(), 700);
				}, 6000);
			}
		};
		if (document.body) show();
		else window.addEventListener("DOMContentLoaded", show);
	};

	if (!window.bbgm || !window.bbgm.toWorker) {
		badge("🎯 Target mod OFF: Football GM didn't load", false);
		return;
	}

	const install = async () => {
		const code = `console.log(JSON.stringify((${wasTargetModInstall.toString()})(${JSON.stringify(WAS_TARGET_SETTINGS)})));`;
		const out = await window.bbgm.toWorker("main", "evalOnWorker", code);
		const lines = String(out ?? "").split("\n").filter((x) => x.trim() !== "");
		return JSON.parse(lines[lines.length - 1]);
	};

	let res = null;
	for (let i = 0; i < 5 && !res; i++) {
		try {
			res = await install();
		} catch (e) {
			await new Promise((resolve) => setTimeout(resolve, 2000));
		}
	}
	if (res && res.ok) {
		badge(WAS_TARGET_SETTINGS.enabled ? `🎯 Realistic Targets ON (v${res.version})` : "🎯 Realistic Targets installed but turned off in settings", true);
		console.log(`Realistic Targets ON (v${res.version}). Targets routed so far: ${res.routed}.`);
	} else {
		const why = (res && res.reason) || "couldn't reach the game engine";
		badge("🎯 Target mod OFF: normal targeting. " + why, false);
		console.log("Realistic Targets OFF: " + why);
	}
})();
