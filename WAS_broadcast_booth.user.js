// ==UserScript==
// @name         Football GM: Broadcast Booth
// @namespace    was-dynasty-fbgm
// @version      1.3.1
// @description  Turns Football GM's live play-by-play into TV-style commentary. Real names, yards, downs, score and in-game stat callbacks; the flavor is made up to fit. Hover any line to see the original. Halftime and postgame shows, NFL-style kickoff windows on the schedule, and a score ticker.
// @match        https://play.football-gm.com/*
// @grant        none
// @inject-into  page
// @sandbox      raw
// @run-at       document-idle
// ==/UserScript==

(() => {
	"use strict";

	// ------------------------------------------------------------------ helpers
	const PREF_KEY = "pgmBroadcastBooth";
	let enabled = true;
	try {
		enabled = localStorage.getItem(PREF_KEY) !== "off";
	} catch {}

	const hash = (s) => {
		let h = 2166136261;
		for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
		return h >>> 0;
	};
	// deterministic pick so the same play always gets the same call
	const picker = (seed) => {
		let n = 0;
		return (arr) => arr[hash(seed + "#" + n++) % arr.length];
	};
	const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
	const SUFFIX = new Set(["Jr.", "Sr.", "II", "III", "IV", "V"]);
	const last = (full) => {
		const parts = full.trim().split(/\s+/);
		if (parts.length >= 3 && SUFFIX.has(parts[parts.length - 1])) return parts.slice(-2).join(" ");
		return parts[parts.length - 1];
	};
	const ORD = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"];
	const ordWord = (n) => ORD[n] ?? `${n}th`;
	const numWord = (n) => ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"][n] ?? String(n);
	const B = (s) => `<b>${esc(s)}</b>`;
	const stripStats = (t) => t.replace(/\s*\((?:\d+ [A-Z][A-Za-z]+(?:, )?)+\)/g, "").trim();

	// ------------------------------------------------------------------ team names
	const teamNames = {};
	let namesLoaded = false;
	const loadTeamNames = async () => {
		if (namesLoaded) return;
		try {
			const out = await window.bbgm.toWorker("main", "evalOnWorker", 'console.log(JSON.stringify(bbgm.g.get("teamInfoCache").map((t) => [t.abbrev, t.name])))');
			for (const [a, n] of JSON.parse(out)) teamNames[a] = n;
			namesLoaded = true;
		} catch {}
	};
	const nick = (abbrev) => teamNames[abbrev] || abbrev;

	// ------------------------------------------------------------------ reading an entry
	const info = new WeakMap(); // entry element -> parsed info

	const readEntry = (el) => {
		if (info.has(el)) return info.get(el);
		const img = el.querySelector(":scope > div > img");
		const body = el.querySelector(":scope > .flex-grow-1");
		if (!body) return null;
		const kids = [...body.childNodes];
		let start = 0;
		if (kids[0] && kids[0].nodeType === 1 && kids[0].tagName === "DIV" && kids[0].classList.contains("d-flex")) start = 1;
		const scoreDiv = kids.length > start && kids[kids.length - 1].nodeType === 1 && kids[kids.length - 1].tagName === "DIV" ? kids[kids.length - 1] : null;
		const mid = kids.slice(start, scoreDiv ? -1 : undefined);
		const orig = mid.map((n) => n.textContent).join("").replace(/\s+/g, " ").trim();
		let score = null;
		if (scoreDiv) {
			const bold = scoreDiv.querySelector("b");
			const other = scoreDiv.querySelector(".text-body-secondary");
			if (bold && other) score = { mine: Number(bold.textContent), theirs: Number(other.textContent) };
		}
		const r = { el, body, mid, scoreDiv, t: img ? img.alt : null, orig, score, textOnly: body.classList.contains("fw-bold") };
		// down-and-distance rows: "13:12" <b>1st & 10</b> <span>50 yd line</span>
		const bold = mid.find((n) => n.nodeType === 1 && n.tagName === "SPAN" && n.classList.contains("fw-bold"));
		const clockNode = mid.find((n) => n.nodeType === 3 && /^\s*\d{1,2}:\d{2}\s*$/.test(n.nodeValue));
		if (bold && clockNode) {
			const dd = /^(1st|2nd|3rd|4th) & (goal|\d+)$/.exec(bold.textContent.trim());
			const spotNode = bold.nextSibling;
			if (dd) {
				r.header = { clock: clockNode.nodeValue.trim(), down: Number(dd[1][0]), toGo: dd[2] === "goal" ? null : Number(dd[2]), goal: dd[2] === "goal", spot: spotNode ? spotNode.textContent.trim() : "" };
			} else if (/Kick off/i.test(bold.textContent)) {
				r.header = { clock: clockNode.nodeValue.trim(), kickoff: true };
			}
		}
		info.set(el, r);
		return r;
	};

	// ------------------------------------------------------------------ game context from older entries
	const context = (el) => {
		const ctx = { header: null, offense: null, quarter: 1, ot: false, score: {}, teams: new Set(), tally: newTally() };
		const older = [];
		for (let x = el.nextElementSibling; x; x = x.nextElementSibling) older.push(x);
		older.reverse(); // oldest first
		for (const x of older) {
			const r = readEntry(x);
			if (!r) continue;
			if (r.t) ctx.teams.add(r.t);
			if (r.header) {
				ctx.header = r.header;
				ctx.offense = r.t;
			}
			const q = /^Start of (\d)(?:st|nd|rd|th) quarter/.exec(r.orig);
			if (q) ctx.quarter = Number(q[1]);
			if (/^Start of .*overtime/.test(r.orig)) ctx.ot = true;
			if (r.score && r.t) {
				// a safety's score block belongs to the defense, not the team whose logo is on the line
				const scorer = /safety/i.test(r.orig) ? [...ctx.teams].find((x) => x !== r.t) : r.t;
				if (scorer) {
					ctx.score[scorer] = r.score.mine;
					ctx.scoredLast = scorer;
					ctx.otherScore = r.score.theirs;
				}
			}
			addToTally(ctx.tally, r);
		}
		const r = readEntry(el);
		if (r && r.t) ctx.teams.add(r.t);
		ctx.teamList = [...ctx.teams];
		const opp = (t) => ctx.teamList.find((x) => x !== t);
		// fill the other team's score from the last score block
		if (ctx.scoredLast) {
			const o = opp(ctx.scoredLast);
			if (o !== undefined) ctx.score[o] = ctx.otherScore;
		}
		ctx.opp = opp;
		ctx.pts = (t) => ctx.score[t] ?? 0;
		return ctx;
	};

	const newTally = () => ({ td: {}, passTd: {}, int: {}, intThrown: {}, sack: {}, ff: {}, fg: {}, rush: {}, rec: {}, pass: {} });
	const inc = (o, k, n = 1) => (o[k] = (o[k] ?? 0) + n);
	const addToTally = (T, r) => {
		const s = stripStats(r.orig);
		let m;
		if ((m = /^(.+) completed a pass to (.+) for (-?\d+) yards?( and a touchdown!)?$/.exec(s)) || (m = /^(.+) completed a pass to (.+) for a touchdown!$/.exec(s))) {
			const yds = m[3] !== undefined && !Number.isNaN(Number(m[3])) ? Number(m[3]) : 0;
			inc(T.pass, m[1], yds);
			inc(T.rec, m[2], yds);
			if (/touchdown/.test(s)) {
				inc(T.td, m[2]);
				inc(T.passTd, m[1]);
			}
		} else if ((m = /^(.+) rushed for (-?\d+) yards?( and a touchdown!)?$/.exec(s))) {
			inc(T.rush, m[1], Number(m[2]));
			if (m[3]) inc(T.td, m[1]);
		} else if ((m = /^Intercepted by (.+)!$/.exec(s))) {
			inc(T.int, m[1]);
			T.lastQB && inc(T.intThrown, T.lastQB);
		} else if ((m = /^(.+) was sacked by (.+) for a/.exec(s))) {
			inc(T.sack, m[2]);
		} else if ((m = /fumbled the ball! Forced fumble by (.+)$/.exec(s))) {
			inc(T.ff, m[1]);
		} else if ((m = /^(.+) made a (\d+) yard field goal$/.exec(s))) {
			inc(T.fg, m[1]);
		} else if ((m = /^(.+) (?:returned|recovered) .* for a touchdown!$/.exec(s)) || (m = /^Turnover! (.+) recovered the fumble .*touchdown!$/.exec(s))) {
			inc(T.td, m[1]);
		}
		if ((m = /^(.+) drops back to pass$/.exec(s))) T.lastQB = m[1];
	};

	// ------------------------------------------------------------------ the calls
	const situation = (ctx) => {
		const h = ctx.header;
		const off = ctx.offense;
		const late = (ctx.quarter >= 4 || ctx.ot) && h && h.clock && toSec(h.clock) <= 300;
		const diff = off ? ctx.pts(off) - ctx.pts(ctx.opp(off)) : 0;
		return { h, off, late, close: Math.abs(diff) <= 8, diff, redzone: h && redZone(h.spot, off) };
	};
	const toSec = (c) => {
		const [m, s] = c.split(":").map(Number);
		return m * 60 + s;
	};
	const redZone = (spot, off) => {
		if (!spot || !off) return false;
		const m = /^([A-Z0-9]+) (\d+)$/.exec(spot);
		return !!m && m[1] !== off && Number(m[2]) <= 20;
	};
	const firstDown = (ctx, yds) => {
		const h = ctx.header;
		return h && !h.goal && h.toGo !== null && yds >= h.toGo;
	};

	const callFor = (r, ctx) => {
		const p = picker(r.orig + "|" + (ctx.header ? ctx.header.clock : "") + "|" + ctx.quarter);
		const S = situation(ctx);
		const T = ctx.tally;
		const s = stripStats(r.orig);
		let m;
		const fdTag = (yds) => {
			const h = ctx.header;
			if (!h || h.goal) return "";
			if (firstDown(ctx, yds)) {
				if (h.down === 4) return " " + p(["They convert on fourth down!", "Fourth-down conversion — huge!", "And they pick it up on fourth down!"]);
				if (h.down === 3) return " " + p(["Third down converted.", "That moves the chains on third down.", "First down — a big conversion."]);
				return yds >= 10 ? " " + p(["First down.", "Moves the chains.", ""]) : "";
			}
			if (h.down === 3 && yds < h.toGo) return " " + p([`Short of the sticks — ${h.toGo - yds > 0 ? `fourth and ${h.toGo - yds}` : "fourth down"} coming up.`, "Not enough for the first down.", "Just short on third down."]);
			if (h.down === 4 && yds < h.toGo) return " " + p(["Short of the marker!", "They come up short on fourth down!", "Stopped short!"]);
			return "";
		};
		const milestone = (book, name, before, add, marks) => {
			for (const mk of marks) if (before < mk && before + add >= mk) return ` That's ${mk} ${book} yards on the day for ${last(name)}.`;
			return "";
		};
		const scoreLine = () => {
			if (!r.score || !r.t) return "";
			const scorer = /safety/i.test(s) ? ctx.opp(r.t) : r.t;
			if (!scorer) return "";
			const o = ctx.opp(scorer);
			const mine = r.score.mine;
			const theirs = r.score.theirs;
			const before = ctx.pts(scorer);
			if (mine > theirs && before <= theirs) return ` ${nick(scorer)} take the lead, ${mine}-${theirs}!`;
			if (mine === theirs) return ` We're all tied up at ${mine}!`;
			if (mine > theirs) return ` ${nick(scorer)} up ${mine}-${theirs}.`;
			return ` ${nick(o)} still lead, ${theirs}-${mine}.`;
		};
		const clutch = S.late && S.close;
		const tp = picker(r.orig + "|tackle"); // own picker, so filling in the tackler later doesn't reshuffle the rest of the call
		const tackleTag = () => {
			const a = r.attrib;
			if (!a) return "";
			if (a.solo.length === 1) return " " + tp([`${last(a.solo[0])} makes the tackle.`, `Brought down by ${last(a.solo[0])}.`, `${last(a.solo[0])} wraps him up.`]);
			if (a.ast.length >= 2) return " " + tp([`${last(a.ast[0])} and ${last(a.ast[1])} bring him down.`, `Gang tackle, ${last(a.ast[0])} and ${last(a.ast[1])}.`]);
			if (a.ast.length === 1) return ` ${last(a.ast[0])} in on the stop.`;
			return "";
		};

		// ---- passing
		if ((m = /^(.+) drops back to pass$/.exec(s))) {
			const qb = last(m[1]);
			if (S.h && S.h.down >= 3 && clutch) return p([`${qb} drops back… this is the play…`, `Big snap here. ${qb} drops back…`, `${qb} in the shotgun, everything on the line…`]);
			return p([`${qb} drops back…`, `${qb} takes the snap, looks downfield…`, `${qb} in the shotgun, drops back…`, `Snap to ${qb}, he's looking…`]);
		}
		if ((m = /^(.+) completed a pass to (.+) for (-?\d+) yards?( and a touchdown!)?$/.exec(s)) || (m = /^(.+) completed a pass to (.+) for a touchdown!$/.exec(s))) {
			const qb = last(m[1]);
			const wr = last(m[2]);
			const td = /touchdown/.test(s);
			const yds = m[3] !== undefined && /^-?\d+$/.test(m[3]) ? Number(m[3]) : 0;
			if (td) {
				const n = (T.td[m[2]] ?? 0) + 1;
				const qn = (T.passTd[m[1]] ?? 0) + 1;
				let line;
				if (yds >= 40) line = p([`${qb} lets it fly deep… ${wr} has a step… he's GOT IT! ${yds} yards, TOUCHDOWN!`, `${qb} goes for the home run ball — ${wr} hauls it in and he's GONE! ${yds}-yard touchdown!`, `Deep shot down the sideline… CAUGHT! ${wr} takes it ${yds} yards to the house!`]);
				else if (yds >= 15) line = p([`${qb} fires to ${wr}… TOUCHDOWN! ${yds} yards!`, `${qb} threads it into ${wr} in the end zone — TOUCHDOWN!`, `${wr} beats his man, ${qb} puts it right on him — ${yds}-yard touchdown!`]);
				else line = p([`${qb} finds ${wr} in the end zone — TOUCHDOWN!`, `Quick throw to ${wr}… he's in! Touchdown!`, `${qb} to ${wr}, short and sweet — TOUCHDOWN!`]);
				const extra = n >= 2 ? ` That's ${wr}'s ${ordWord(n)} touchdown of the game!` : qn >= 2 ? ` ${qb}'s ${ordWord(qn)} touchdown pass today.` : "";
				return { html: `<span class="text-success fw-bold">${esc(line)}</span>${esc(extra + scoreLine())}`, big: true };
			}
			const before = T.rec[m[2]] ?? 0;
			const qbBefore = T.pass[m[1]] ?? 0;
			let line;
			if (yds < 0) line = p([`Screen to ${wr} goes nowhere — loss of ${-yds}.`, `${wr} catches it behind the line and gets swarmed, loss of ${-yds}.`]);
			else if (yds === 0) line = p([`Checkdown to ${wr}, and he's dropped right there. No gain.`, `${wr} makes the catch but goes nowhere. No gain.`]);
			else if (yds <= 3) line = p([`Checkdown to ${wr}, just ${yds} yard${yds === 1 ? "" : "s"}.`, `Quick dump-off to ${wr} in the flat for ${yds}.`, `${qb} hits ${wr} underneath, gets ${yds}.`]);
			else if (yds <= 9) line = p([`${qb} to ${wr} on a quick out, ${yds} yards.`, `Slant to ${wr}, good for ${yds}.`, `${qb} hits ${wr} on the hitch, ${yds} yards.`, `${wr} hauls it in for ${yds}.`]);
			else if (yds <= 19) line = p([`${qb} fires a bullet to ${wr} on the dig — ${yds} yards!`, `Comeback route to ${wr} outside the numbers, ${yds} yards.`, `${qb} finds ${wr} over the middle for ${yds}.`, `Nice throw and catch, ${wr} for ${yds}.`]);
			else if (yds <= 34) line = p([`${qb} drops it in the bucket to ${wr} — ${yds} yards!`, `Big chunk play! ${wr} up the seam for ${yds}!`, `${qb} hits ${wr} in stride — ${yds}-yard gain!`]);
			else line = p([`${qb} airs it out… ${wr} makes the catch! ${yds} yards!`, `HUGE play! ${wr} gets behind the defense — ${yds} yards!`, `Deep ball to ${wr}… CAUGHT! A ${yds}-yard strike!`]);
			const extra = milestone("receiving", m[2], before, yds, [100, 150, 200]) || milestone("passing", m[1], qbBefore, yds, [300, 400]);
			return { html: esc(line + tackleTag() + fdTag(yds) + extra), big: yds >= 25 };
		}
		if ((m = /^Incomplete pass to (.+)$/.exec(s))) {
			const wr = last(m[1]);
			const pd = r.attrib && r.attrib.pd.length === 1 ? last(r.attrib.pd[0]) : null;
			if (S.h && S.h.down === 4) {
				if (pd) return { html: `<b>${esc(tp([`Fourth-down throw for ${wr}… BROKEN UP by ${pd}! Huge stop!`, `${pd} gets a hand on it on fourth down! Incomplete for ${wr}!`]))}</b>`, big: true };
				return { html: `<b>${esc(p([`Fourth-down throw for ${wr}… INCOMPLETE!`, `It's thrown for ${wr}… no! Falls incomplete on fourth down!`, `${wr} can't come up with it on fourth down!`]))}</b>`, big: true };
			}
			if (pd) return { html: `<b>${esc(tp([`BROKEN UP by ${pd}! Intended for ${wr}.`, `${pd} gets a hand in there — incomplete!`, `${pd} breaks it up! ${wr} had no chance.`, `Great coverage by ${pd}, knocks it away from ${wr}.`]))}</b>` };
			return p([`Thrown for ${wr}… incomplete.`, `Overthrown — ${wr} couldn't get to it.`, `Off target, incomplete for ${wr}.`, `Off the fingertips of ${wr}, incomplete.`, `${wr} can't come up with it.`]);
		}
		if ((m = /^Intercepted by (.+)!$/.exec(s))) {
			const d = last(m[1]);
			const n = (T.int[m[1]] ?? 0) + 1;
			const qb = T.lastQB ? last(T.lastQB) : "The quarterback";
			const qn = T.lastQB ? (T.intThrown[T.lastQB] ?? 0) + 1 : 1;
			let line = p([`${qb} throws… PICKED OFF! ${m[1]} jumps the route!`, `INTERCEPTED! ${d} reads it all the way!`, `${qb} forces it… and ${d} takes it away!`, `Bad decision! ${d} steps in front — INTERCEPTION!`]);
			if (clutch) line = `${line} What a moment for it!`;
			const extra = n >= 2 ? ` That's ${d}'s ${ordWord(n)} pick of the game!` : qn >= 2 ? ` ${qb}'s ${ordWord(qn)} interception today.` : "";
			return { html: `<span class="text-danger fw-bold">${esc(line)}</span>${esc(extra)}`, big: true };
		}
		if ((m = /^(.+) returned the interception (-?\d+) yards?( for a touchdown!)?$/.exec(s))) {
			const d = last(m[1]);
			const yds = Number(m[2]);
			if (m[3]) return { html: `<span class="text-success fw-bold">${esc(p([`${d} is gone! PICK-SIX! ${yds} yards to the house!`, `He's got nothing but grass! ${d} takes it back ${yds} for the touchdown!`]))}</span>${esc(scoreLine())}`, big: true };
			if (yds >= 20) return p([`${d} weaves through traffic — ${yds}-yard return!`, `And ${d} brings it back ${yds} yards!`]);
			if (yds <= 0) return p([`${d} is wrapped up right where he caught it.`, `${d} goes down with it. No return.`]);
			return p([`${d} returns it ${yds}.`, `${d} is brought down after ${yds} on the return.`]);
		}
		if ((m = /^(.+) stays in the endzone for a touchback$/.exec(s))) return `${last(m[1])} takes a knee in the end zone. Touchback.`;

		// ---- sacks
		if ((m = /^(.+) was sacked by (.+) for a (\d+) yard loss$/.exec(s))) {
			const qb = last(m[1]);
			const d = last(m[2]);
			const yds = Number(m[3]);
			const n = (T.sack[m[2]] ?? 0) + 1;
			const big = (S.h && S.h.down >= 3) || clutch;
			let line = p([`${d} gets home! ${qb} goes down for a loss of ${yds}!`, `SACK! ${d} beats his man and drops ${qb}, minus ${yds}.`, `${qb} has nowhere to go — ${d} brings him down! Loss of ${yds}.`, `${d} off the edge — ${qb} never saw him! Sacked for ${yds}.`]);
			if (n >= 2) line += ` That's ${d}'s ${ordWord(n)} sack of the day!`;
			return big ? { html: `<b>${esc(line)}</b>`, big } : line;
		}
		if ((m = /^(.+) was sacked by (.+) for a safety!$/.exec(s))) return { html: `<span class="text-danger fw-bold">${esc(`${last(m[2])} drops ${last(m[1])} in the end zone — SAFETY!`)}</span>${esc(scoreLine())}`, big: true };

		// ---- runs
		if ((m = /^(.+) hands the ball off to (.+)$/.exec(s))) return p([`Handoff to ${last(m[2])}…`, `${last(m[1])} gives it to ${last(m[2])}…`, `${last(m[2])} takes the handoff…`]);
		if ((m = /^(.+) rushed for (-?\d+) yards?( and a touchdown!)?$/.exec(s)) || (m = /^(.+) rushed for a touchdown!$/.exec(s))) {
			const rb = last(m[1]);
			const yds = m[2] !== undefined && /^-?\d+$/.test(m[2]) ? Number(m[2]) : 0;
			if (/touchdown/.test(s)) {
				const n = (T.td[m[1]] ?? 0) + 1;
				let line;
				if (yds >= 30) line = p([`${rb} breaks into the open — nobody's catching him! ${yds}-yard TOUCHDOWN!`, `${rb} hits the hole and he's GONE! ${yds} yards to the house!`]);
				else if (yds >= 6) line = p([`${rb} cuts back, finds a crease — TOUCHDOWN! ${yds} yards!`, `${rb} bounces it outside and walks in! Touchdown!`]);
				else line = p([`${rb} plows ahead… he's IN! Touchdown!`, `Give it to ${rb} — he pushes the pile and scores!`, `${rb} punches it in from ${yds}!`]);
				const extra = n >= 2 ? ` That's ${rb}'s ${ordWord(n)} touchdown today!` : "";
				return { html: `<span class="text-success fw-bold">${esc(line)}</span>${esc(extra + scoreLine())}`, big: true };
			}
			const before = T.rush[m[1]] ?? 0;
			let line;
			if (yds < 0) line = p([`${rb} is hit in the backfield — loss of ${-yds}.`, `Blown up behind the line! ${rb} loses ${-yds}.`, `${rb} gets dropped for a loss of ${-yds}.`]);
			else if (yds === 0) line = p([`${rb} is stuffed at the line, no gain.`, `Nothing there — ${rb} gets stopped cold.`, `${rb} runs into a wall. No gain.`]);
			else if (yds <= 3) line = p([`${rb} grinds out ${yds}.`, `${rb} falls forward for ${yds}.`, `Short gain, ${rb} for ${yds}.`]);
			else if (yds <= 9) line = p([`${rb} finds a crease for ${yds}.`, `${rb} cuts back and picks up ${yds}.`, `Nice run by ${rb}, ${yds} yards.`, `${rb} slips a tackle, gains ${yds}.`]);
			else if (yds <= 19) line = p([`${rb} bursts through the hole — ${yds} yards!`, `${rb} breaks into the second level for ${yds}!`, `Big run! ${rb} for ${yds}.`]);
			else line = p([`${rb} breaks LOOSE! ${yds} yards before they finally drag him down!`, `${rb} hits the hole and he's off — a ${yds}-yard run!`, `Huge run! ${rb} rips off ${yds}!`]);
			return { html: esc(line + tackleTag() + fdTag(yds) + milestone("rushing", m[1], before, yds, [100, 150, 200])), big: yds >= 20 };
		}
		if ((m = /^(.+) kneels$/.exec(s))) return p([`${last(m[1])} takes a knee.`, `Victory formation — ${last(m[1])} kneels it.`]);
		if ((m = /^(.+) was tackled in the endzone for a safety!$/.exec(s))) return { html: `<span class="text-danger fw-bold">${esc(`${last(m[1])} is dropped in the end zone — SAFETY!`)}</span>${esc(scoreLine())}`, big: true };

		// ---- fumbles
		if ((m = /^(.+) fumbled the ball! Forced fumble by (.+)$/.exec(s))) {
			const c = last(m[1]);
			const d = last(m[2]);
			return { html: `<b>${esc(p([`${d} comes flying in and BLOWS UP ${c} — the ball is OUT!`, `${d} punches it loose! FUMBLE!`, `${c} gets drilled by ${d} — the ball's on the turf!`, `FUMBLE! ${d} rips it right out of ${c}'s hands!`]))}</b>`, big: true };
		}
		if ((m = /^Turnover! (.+) recovered the fumble (?:and returned it (-?\d+) yards?( for a touchdown!)?|in the endzone for a touchdown!)$/.exec(s))) {
			const d = last(m[1]);
			if (/touchdown/.test(s)) return { html: `<span class="text-success fw-bold">${esc(`${d} scoops it up and he's GONE! FUMBLE RETURN TOUCHDOWN!`)}</span>${esc(scoreLine())}`, big: true };
			return { html: `<span class="text-danger fw-bold">${esc(p([`Scramble for it… ${d} comes up with it! TURNOVER!`, `${d} falls on it! The defense takes it away!`, `${d} scoops it up! Change of possession!`]))}</span>`, big: true };
		}
		if ((m = /^Turnover! (.+) recovered the fumble in the endzone, resulting in a (safety!|touchback)$/.exec(s))) return { html: `<span class="text-danger fw-bold">${esc(`${last(m[1])} falls on it in the end zone — ${m[2] === "touchback" ? "touchback" : "SAFETY"}!`)}</span>`, big: true };
		if ((m = /^(.+) recovered the fumble( and carried it into the endzone for a touchdown!)?$/.exec(s))) {
			if (m[2]) return { html: `<span class="text-success fw-bold">${esc(`${last(m[1])} picks it up and walks into the end zone! Touchdown!`)}</span>${esc(scoreLine())}`, big: true };
			return p([`${last(m[1])} jumps on his own fumble. Phew.`, `${last(m[1])} recovers! They keep it.`, `They get lucky — ${last(m[1])} falls on it.`]);
		}

		// ---- kicking game
		if ((m = /^(.+) kicked off (?:to the (\d+) yard line|into the end zone|for a touchback)$/.exec(s))) {
			if (/touchback/.test(s)) return p([`${last(m[1])} boots it out of the end zone. Touchback.`, `Big leg from ${last(m[1])} — touchback.`]);
			return p([`${last(m[1])} kicks it away${m[2] ? `, fielded at the ${m[2]}` : " deep into the end zone"}.`, `Here's the kick from ${last(m[1])}…`]);
		}
		if ((m = /^(.+) returned the kickoff (\d+) yards?( for a touchdown!)?$/.exec(s))) {
			const k = last(m[1]);
			const yds = Number(m[2]);
			if (m[3]) return { html: `<span class="text-success fw-bold">${esc(`${k} takes it… finds a seam… he's GONE! KICKOFF RETURN TOUCHDOWN!`)}</span>${esc(scoreLine())}`, big: true };
			if (yds >= 40) return { html: `<b>${esc(p([`${k} breaks a tackle and he's off — ${yds}-yard return!`, `What a return by ${k}! ${yds} yards!`]))}</b>`, big: true };
			if (yds <= 5) return p([`${k} is swallowed up right away.`, `${k} doesn't get far, ${yds} yard${yds === 1 ? "" : "s"}.`]);
			return p([`${k} brings it out ${yds} yards.`, `${k} returns it ${yds}.`]) + tackleTag();
		}
		if (s === "The punt team takes the field") return p(["Punt team trots out.", "They'll punt it away.", "Here comes the punt unit."]);
		if ((m = /^(.+) punted (\d+) yards?( for a touchback| into the end zone)?$/.exec(s))) {
			const k = last(m[1]);
			const yds = Number(m[2]);
			if (m[3]) return `${k} hangs it up… into the end zone. Touchback.`;
			if (yds >= 50) return p([`${k} gets all of it — a ${yds}-yard boomer!`, `What a punt by ${k}, ${yds} yards!`]);
			return p([`${k} punts it ${yds} yards.`, `${k} with a ${yds}-yard punt.`]);
		}
		if ((m = /^(.+) returned the punt (-?\d+) yards?( for a touchdown!)?$/.exec(s))) {
			const k = last(m[1]);
			const yds = Number(m[2]);
			if (m[3]) return { html: `<span class="text-success fw-bold">${esc(`${k} fields it, makes one guy miss… he's GONE! PUNT RETURN TOUCHDOWN!`)}</span>${esc(scoreLine())}`, big: true };
			if (yds === 0) return p([`${k} is swarmed immediately, no return.`, `No room for ${k}, tackled right there.`]);
			if (yds >= 25) return { html: `<b>${esc(p([`${k} makes a man miss — ${yds}-yard return!`, `Big return by ${k}! ${yds} yards!`]))}</b>`, big: true };
			return p([`${k} returns it ${yds}.`, `${k} brings it back ${yds} yards.`]) + tackleTag();
		}
		if ((m = /^(.+) comes on for a (\d+) yard field goal attempt$/.exec(s))) {
			const k = last(m[1]);
			if (clutch) return { html: `<b>${esc(p([`${k} trots out for a ${m[2]}-yarder… pressure's on.`, `Here's ${k} from ${m[2]}. Big kick.`]))}</b>`, big: true };
			return p([`${k} out for a ${m[2]}-yard try.`, `They'll send out ${k} from ${m[2]}.`]);
		}
		if ((m = /^(.+) (made|missed) a (\d+) yard field goal$/.exec(s))) {
			const k = last(m[1]);
			const yds = Number(m[3]);
			if (m[2] === "made") {
				const n = (T.fg[m[1]] ?? 0) + 1;
				const line = yds >= 50 ? p([`${k} lines it up from ${yds}… it's got the distance… IT'S GOOD!`, `From ${yds}… BOOM! ${k} nails it!`]) : p([`${k}'s kick is up… and it's good from ${yds}.`, `${k} drills it from ${yds}.`, `Right down the middle, ${k} from ${yds}.`]);
				const extra = n >= 3 ? ` That's ${k}'s ${ordWord(n)} field goal today.` : "";
				return { html: `<span class="text-success">${esc(line)}</span>${esc(extra + scoreLine())}`, big: clutch };
			}
			return { html: `<span class="text-danger fw-bold">${esc(p([`${k} from ${yds}… NO GOOD!`, `${k}'s kick is… wide! Missed from ${yds}!`, `${k} pushes it — no good from ${yds}!`]))}</span>`, big: true };
		}
		if ((m = /^(.+) comes on for an extra point attempt$/.exec(s))) return p([`${last(m[1])} on for the extra point.`, `Point after, ${last(m[1])}.`]);
		if ((m = /^(.+) (made|missed) the extra point$/.exec(s))) {
			if (m[2] === "made") return { html: esc(p([`Extra point is good.`, `${last(m[1])} adds the point.`]) + scoreLine()) };
			return { html: `<span class="text-danger fw-bold">${esc(p([`The extra point is… NO GOOD! ${last(m[1])} misses!`, `Missed PAT by ${last(m[1])}! That could loom large.`]))}</span>${esc(scoreLine())}`, big: true };
		}
		if ((m = /^(.+) completed a pass to (.+) for a two-point conversion!$/.exec(s))) return { html: `<span class="text-success fw-bold">${esc(p([`${last(m[1])} finds ${last(m[2])} — the two-point try is GOOD!`, `${last(m[2])} hauls it in! Two-point conversion!`]))}</span>${esc(scoreLine())}`, big: true };
		if ((m = /^(.+) rushed for a two-point conversion!$/.exec(s))) return { html: `<span class="text-success fw-bold">${esc(p([`${last(m[1])} pushes in for two! Conversion is good!`, `${last(m[1])} gets in — two-point conversion!`]))}</span>${esc(scoreLine())}`, big: true };
		if (s === "Two-point conversion attempt") return { html: `<b>${esc("They're going for two!")}</b>` };
		if (s === "Two-point conversion failed") return { html: `<span class="text-danger fw-bold">${esc("No good! The two-point try fails.")}</span>` };
		if ((m = /^(.+) gets ready to attempt an onside kick$/.exec(s))) return { html: `<b>${esc(`Everybody knows it's coming — ${last(m[1])} lines up the onside kick…`)}</b>`, big: true };
		if (/^The onside kick was recovered by the kicking team!$/.test(s)) return { html: `<span class="text-success fw-bold">${esc("THEY GOT IT! The kicking team recovers the onside kick!")}</span>`, big: true };
		if (/^The onside kick was recovered by the receiving team/.test(s)) return /touchdown/.test(s) ? { html: `<span class="text-success fw-bold">${esc("Recovered by the receiving team… and taken all the way back for a TOUCHDOWN!")}</span>`, big: true } : "Recovered by the receiving team. That should do it.";

		// ---- fourth down / flags / clock / injuries
		if (s === "The offense stays on the field, they're going for it on 4th down!") {
			const h = S.h;
			const parts = [`${nick(S.off)} are going for it`];
			if (h) parts[0] += ` on 4th & ${h.goal ? "goal" : h.toGo}`;
			let tail = "!";
			if (S.late && S.diff < 0 && S.diff >= -8) tail = `, down ${-S.diff} with ${h.clock} left. Everything on this snap!`;
			else if (S.late && S.diff < -8) tail = `, down ${-S.diff} with ${h.clock} left. Just playing it out now.`;
			else if (S.late && S.diff > 0) tail = ` with ${h.clock} left, up ${S.diff}. Gutsy!`;
			else if (S.late) tail = ` with ${h.clock} left. Gutsy!`;
			return { html: `<b>${esc(parts[0] + tail)}</b>`, big: true };
		}
		if (s === "Turnover on downs") return { html: `<span class="text-danger fw-bold">${esc(p(["Turnover on downs!", "They don't get it — turnover on downs!"]))}</span>`, big: true };
		if (s === "Flag on the play") return p(["Flag on the play…", "There's a flag down.", "Yellow laundry on the field…"]);
		if ((m = /^Penalty - (.+?)(?: on (.+?))? - (accepted|declined|enforced|overruled)$/.exec(s))) {
			const who = m[2] ? ` on ${last(m[2])}` : "";
			const name = m[1].charAt(0).toUpperCase() + m[1].slice(1);
			if (m[3] === "declined" || m[3] === "overruled") return `${name}${who}, but it's declined.`;
			return p([`${name}${who}. That'll be enforced.`, `The flag is for ${m[1]}${who}. Accepted.`, `${name}${who} — that one's accepted.`]);
		}
		if ((m = /^There are (\d+) (offsetting )?penalties on the play/.exec(s))) return m[2] ? "Flags on both sides — offsetting penalties, replay the down." : `${numWord(Number(m[1]))[0].toUpperCase() + numWord(Number(m[1])).slice(1)} flags on the play.`;
		if ((m = /^Timeout, (offense|defense) \((\d+) remaining\)( to stop the clock)?$/.exec(s))) {
			const team = m[1] === "offense" ? S.off : S.off && ctx.opp(S.off);
			const left = Number(m[2]);
			return `${team ? nick(team) : "They"} call timeout${m[3] ? " to stop the clock" : ""} — ${left === 0 ? "that's their last one" : `${numWord(left)} left`}.`;
		}
		if ((m = /^([A-Z]{1,2}) (.+) was injured!$/.exec(s))) return { html: `<span class="text-warning-emphasis">${esc(p([`Trainers are out — ${m[1]} ${m[2]} is down and being looked at.`, `${m[1]} ${last(m[2])} is hurt on the play. Not what you want to see.`, `Injury timeout — ${m[2]} (${m[1]}) is slow to get up.`]))}</span>` };
		if (s === "Two minute warning" || (m = /^Start of (\d)(?:st|nd|rd|th) quarter$/.exec(s)) || s === "End of game" || /^Start of .*overtime$/.test(s)) {
			const [a, b] = ctx.teamList;
			const sc = a && b ? (ctx.pts(a) >= ctx.pts(b) ? `${nick(a)} ${ctx.pts(a)}, ${nick(b)} ${ctx.pts(b)}` : `${nick(b)} ${ctx.pts(b)}, ${nick(a)} ${ctx.pts(a)}`) : "";
			if (s === "Two minute warning") return `Two-minute warning. ${sc ? `${sc}.` : ""}`;
			if (s === "End of game") {
				if (!(a && b)) return "That's the ballgame!";
				const tied = ctx.pts(a) === ctx.pts(b);
				return tied ? `That's the ballgame — it ends in a tie, ${ctx.pts(a)}-${ctx.pts(b)}.` : `That's the ballgame! Final: ${sc}.`;
			}
			if (m && m[1] === "3") return `Second half is underway. ${sc ? `${sc}.` : ""}`;
			if (m) return `We're into the ${ordWord(Number(m[1]))} quarter. ${sc ? `${sc}.` : ""}`;
			return `We're going to overtime! ${sc ? `${sc}.` : ""}`;
		}
		return null; // unknown line: leave Football GM's text alone
	};

	// ------------------------------------------------------------------ rewriting the DOM
	const apply = (r) => {
		if (r.call !== undefined) return;
		r.call = null;
		if (r.header || !r.orig) return;
		let c;
		try {
			c = callFor(r, context(r.el));
		} catch (e) {
			console.log("Broadcast Booth: " + e.message);
			c = null;
		}
		if (!c) return;
		const html = typeof c === "string" ? esc(c) : c.html;
		const span = document.createElement("span");
		span.className = "pgm-call";
		span.innerHTML = html;
		span.title = r.orig;
		if (r.attrib) span.dataset.by = JSON.stringify(r.attrib);
		r.body.insertBefore(span, r.scoreDiv);
		r.call = span;
		r.saved = r.mid.map((n) => (n.nodeType === 3 ? n.nodeValue : null));
		show(r);
	};
	const show = (r) => {
		if (!r.call) return;
		r.call.style.display = enabled ? "" : "none";
		r.mid.forEach((n, i) => {
			if (n.nodeType === 1) n.style.display = enabled ? "none" : "";
			else if (n.nodeType === 3) n.nodeValue = enabled ? "" : r.saved[i];
		});
	};

	// Football GM's play-by-play doesn't name tacklers or pass defenders, but its live box score counts them.
	// Each time a new line shows up, the box score's new tackles / passes defended are matched to the play they belong to.
	// Runs, returns and incompletions: the stats land with the play's own line. Completions: the tackle lands a beat
	// later (with the next line), so that call gets the tackler filled in a moment after it appears.
	const readDefense = () => {
		const out = {};
		for (const table of document.querySelectorAll("table")) {
			const ths = [...table.querySelectorAll("thead tr:last-child th")];
			if (!ths.some((th) => th.title === "Passes Defended")) continue;
			const col = {};
			let c = 0;
			for (const th of ths) {
				if (th.title) col[th.title] = c;
				c += th.colSpan || 1;
			}
			for (const tr of table.querySelectorAll("tbody tr")) {
				const a = tr.querySelector('a[href*="/player/"]');
				if (!a) continue;
				const tds = tr.children;
				const num = (title) => Number((tds[col[title]] && tds[col[title]].textContent) || 0) || 0;
				out[a.getAttribute("href")] = { name: a.textContent.trim(), pd: num("Passes Defended"), solo: num("Solo Tackles"), ast: num("Assists On Tackles") };
			}
		}
		return out;
	};
	const diffBox = (box, prev) => {
		const a = { pd: [], solo: [], ast: [] };
		for (const [k, v] of Object.entries(box)) {
			const was = prev[k] || { pd: 0, solo: 0, ast: 0 };
			if (v.pd > was.pd) a.pd.push(v.name);
			if (v.solo > was.solo) a.solo.push(v.name);
			if (v.ast > was.ast) a.ast.push(v.name);
		}
		return a;
	};
	const RESULT = /^(Incomplete pass to |.+ completed a pass to .+ for -?\d+ yards?$|.+ rushed for -?\d+ yards?$|.+ returned the (kickoff|punt) -?\d+ yards?$)/;
	const COMPLETION = / completed a pass to /;
	// other lines that can put tackles / passes defended in the box score
	const STATFUL = /( was sacked by | fumbled the ball|recovered the fumble|Intercepted by | returned the interception| returned the fumble| was tackled in the endzone)/;
	const rerender = (r) => {
		if (!r.call) return;
		try {
			const c = callFor(r, context(r.el));
			if (c) r.call.innerHTML = typeof c === "string" ? esc(c) : c.html;
			r.call.dataset.by = JSON.stringify(r.attrib);
		} catch (e) {
			console.log("Broadcast Booth: " + e.message);
		}
	};
	let lastBox = null;
	let pending = null; // a completion waiting for its tackle
	const processAll = (container) => {
		const entries = [...container.children].reverse(); // oldest first
		const fresh = [];
		for (const el of entries) {
			const r = readEntry(el);
			if (r && r.call === undefined) fresh.push(r);
		}
		if (fresh.length === 0) return;
		const box = readDefense();
		if (lastBox) {
			const d = diffBox(box, lastBox);
			const plain = (r) => stripStats(r.orig || "");
			const busy = fresh.filter((r) => !r.header && (RESULT.test(plain(r)) || STATFUL.test(plain(r))));
			const newPending = busy.length === 1 && COMPLETION.test(plain(busy[0])) && busy[0] === fresh[fresh.length - 1] ? busy[0] : null;
			const hadPending = !!pending;
			if (pending) {
				// nothing else in this batch could have made a tackle (a fresh completion's tackle isn't in yet)
				if (busy.length === 0 || newPending) {
					if (d.pd.length || d.solo.length || d.ast.length) {
						pending.attrib = d;
						rerender(pending);
					}
				}
				pending = null;
			}
			if (newPending) pending = newPending;
			else if (!hadPending && busy.length === 1 && RESULT.test(plain(busy[0]))) busy[0].attrib = d;
		}
		lastBox = box;
		for (const r of fresh) apply(r);
		for (const r of fresh) tickerAdvance(r);
		renderTicker();
		fresh.forEach((r, i) => {
			try {
				maybeShow(r, i === fresh.length - 1, container);
			} catch (e) {
				console.log("Broadcast Booth (show): " + e.message);
			}
		});
	};

	// ------------------------------------------------------------------ game-day slots (shared)
	// Runs inside Football GM's worker (embedded with .toString()), so it only touches the worker's `bbgm`.
	// Gives every game of a week a kickoff slot: Thursday Night Football, Sunday 11:00, Sunday 1:00, Sunday Night
	// Football or Monday Night Football. The best matchups by record go primetime. It only uses records from earlier
	// weeks plus a seed from the week's games, so the slots never move once the week starts.
	const pgmWeekFn = async (opts) => {
		const { g, idb, PHASE } = bbgm;
		const season = g.get("season");
		const phase = g.get("phase");
		if (phase !== PHASE.REGULAR_SEASON && phase !== PHASE.AFTER_TRADE_DEADLINE) return null;
		if (opts.season !== undefined && opts.season !== season) return null;
		const teams = (await idb.cache.teams.getAll()).filter((t) => !t.disabled);
		const byTid = new Map(teams.map((t) => [t.tid, t]));
		const games = await idb.getCopies.games({ season }, "noCopyCache");
		const sched = (await idb.cache.schedule.getAll()).filter((s) => s.homeTid >= 0 && s.awayTid >= 0);
		let day = opts.day;
		if (day === undefined && opts.abbrevs) {
			const tids = opts.abbrevs.map((a) => (teams.find((t) => t.abbrev === a) || {}).tid);
			let best = null;
			for (const gm of games) if (tids.every((tid) => gm.teams.some((t) => t.tid === tid)) && (!best || gm.day > best.day)) best = gm;
			if (best) day = best.day;
		}
		const today = sched.length ? Math.min(...sched.map((s) => s.day)) : undefined;
		if (day === undefined) day = today;
		if (day === undefined) return null;
		const days = [...new Set(games.map((x) => x.day).concat(sched.map((x) => x.day)))].sort((a, b) => a - b);
		const week = days.indexOf(day) + 1;
		if (week <= 0) return null;
		const list = [];
		for (const gm of games) {
			if (gm.day !== day) continue;
			list.push({ gid: gm.gid, home: gm.teams[0].tid, away: gm.teams[1].tid, played: true, hp: gm.teams[0].pts, ap: gm.teams[1].pts, hq: gm.teams[0].ptsQtrs || [], aq: gm.teams[1].ptsQtrs || [], ss: gm.scoringSummary || [], ot: gm.overtimes || 0 });
		}
		for (const s of sched) if (s.day === day) list.push({ gid: s.gid, home: s.homeTid, away: s.awayTid, played: false });
		list.sort((a, b) => a.gid - b.gid);
		if (!list.length) return null;
		// records from earlier weeks only
		const rec = new Map(teams.map((t) => [t.tid, [0, 0, 0]]));
		for (const gm of games) {
			if (gm.day >= day) continue;
			const rh = rec.get(gm.teams[0].tid);
			const ra = rec.get(gm.teams[1].tid);
			if (!rh || !ra) continue;
			const hp = gm.teams[0].pts;
			const ap = gm.teams[1].pts;
			if (hp > ap) {
				rh[0]++;
				ra[1]++;
			} else if (hp < ap) {
				rh[1]++;
				ra[0]++;
			} else {
				rh[2]++;
				ra[2]++;
			}
		}
		const prev = new Map();
		for (const ts of await idb.cache.teamSeasons.getAll()) {
			if (ts.season !== season - 1) continue;
			const n = ts.won + ts.lost + (ts.tied || 0);
			if (n > 0) prev.set(ts.tid, (ts.won + (ts.tied || 0) / 2) / n);
		}
		const seed = season + "|" + week + "|" + list.map((x) => x.gid).join(",");
		let h = 2166136261;
		for (let i = 0; i < seed.length; i++) h = Math.imul(h ^ seed.charCodeAt(i), 16777619);
		let st = h >>> 0;
		const rnd = () => {
			st = (st + 0x6d2b79f5) >>> 0;
			let t = st;
			t = Math.imul(t ^ (t >>> 15), t | 1);
			t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
			return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
		};
		const wp = (tid) => {
			const r = rec.get(tid) || [0, 0, 0];
			const pv = prev.has(tid) ? prev.get(tid) : 0.5;
			return (r[0] + r[2] / 2 + 3 * pv) / (r[0] + r[1] + r[2] + 3);
		};
		const ranked = list.map((x) => ({ x, a: wp(x.home) + wp(x.away) + rnd() * 0.35 })).sort((p, q) => q.a - p.a).map((o) => o.x);
		// 0 TNF, 1 Sun 11:00, 2 Sun 1:00, 3 SNF, 4 MNF
		const slotOf = new Map();
		if (ranked.length >= 5) {
			slotOf.set(ranked[0].gid, 3);
			slotOf.set(ranked[1].gid, 4);
			const rest = ranked.slice(2);
			const tnf = rest.splice(Math.floor(rnd() * rest.length), 1)[0];
			slotOf.set(tnf.gid, 0);
			for (let i = rest.length - 1; i > 0; i--) {
				const j = Math.floor(rnd() * (i + 1));
				const tmp = rest[i];
				rest[i] = rest[j];
				rest[j] = tmp;
			}
			const n11 = Math.round(rest.length * 0.4);
			rest.forEach((x, i) => slotOf.set(x.gid, i < n11 ? 1 : 2));
		} else {
			ranked.forEach((x, i) => slotOf.set(x.gid, [3, 2, 4, 1][i] ?? 2));
		}
		// Week 1 kicks off the Thursday after Labor Day
		const ld = new Date(season, 8, 1);
		while (ld.getDay() !== 1) ld.setDate(ld.getDate() + 1);
		const thu = new Date(ld);
		thu.setDate(ld.getDate() + 3 + 7 * (week - 1));
		const add = (d, n) => {
			const x = new Date(d);
			x.setDate(x.getDate() + n);
			return x;
		};
		const fmt = (d) => d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
		const slots = [
			{ key: "TNF", name: "Thursday Night Football", short: "TNF", date: fmt(thu), time: "8:15 PM" },
			{ key: "SUN11", name: "Sunday", short: "SUN 11:00", date: fmt(add(thu, 3)), time: "11:00 AM" },
			{ key: "SUN1", name: "Sunday", short: "SUN 1:00", date: fmt(add(thu, 3)), time: "1:00 PM" },
			{ key: "SNF", name: "Sunday Night Football", short: "SNF", date: fmt(add(thu, 3)), time: "7:30 PM" },
			{ key: "MNF", name: "Monday Night Football", short: "MNF", date: fmt(add(thu, 4)), time: "8:15 PM" },
		];
		const ab = (tid) => (byTid.get(tid) || {}).abbrev;
		return {
			season,
			day,
			week,
			today: day === today,
			userTid: g.get("userTid"),
			slots,
			games: list.map((x) => ({ ...x, slot: slotOf.get(x.gid), homeAbbrev: ab(x.home), awayAbbrev: ab(x.away), homeRec: rec.get(x.home), awayRec: rec.get(x.away) })),
		};
	};
	const weekInfo = async (opts) => JSON.parse(await window.bbgm.toWorker("main", "evalOnWorker", `console.log(JSON.stringify(await (${pgmWeekFn.toString()})(${JSON.stringify(opts)})));`));

	// ------------------------------------------------------------------ halftime & postgame shows
	// When the 2nd quarter ends, the game pauses and a halftime show pops up; at the final whistle, a postgame show.
	// Everything in them comes from what's already happened in this game (the live box score and play-by-play) plus
	// league info that doesn't spoil anything (records going in, other games, leaders through last week).
	const CAST = {
		RICK: ["Rick", "play-by-play", "text-primary"],
		DEKE: ["Deke", "analyst", "text-success"],
		MONICA: ["Monica", "studio", "text-danger"],
	};
	const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;
	const listAnd = (xs) => (xs.length <= 1 ? xs.join("") : xs.length === 2 ? `${xs[0]} and ${xs[1]}` : `${xs.slice(0, -1).join(", ")}, and ${xs[xs.length - 1]}`);
	const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
	const recStr = (r) => (r ? `${r[0]}-${r[1]}${r[2] ? `-${r[2]}` : ""}` : "");

	// ---- the live box score, as it stands right now
	const FIELDS = {
		pass: { cmp: "Completions", att: "Passing Attempts", yds: "Passing Yards", td: "Passing Touchdowns", int: "Interceptions", sk: "Times Sacked" },
		rush: { att: "Rushing Attempts", yds: "Rushing Yards", td: "Rushing Touchdowns", lng: "Longest Run" },
		recv: { tgt: "Targets", rec: "Receptions", yds: "Receiving Yards", td: "Receiving Touchdowns", lng: "Longest Reception" },
		def: { solo: "Solo Tackles", ast: "Assists On Tackles", tck: "Total Tackles", tfl: "Tackles For Loss", sk: "Sacks", pd: "Passes Defended", int: "Interceptions", intTD: "Interceptions returned for touchdowns", ff: "Forced Fumbles", fr: "Fumbles Recovered", frTD: "Fumbles returned for touchdowns" },
		kick: { fgm: "Field Goals Made", fga: "Field Goals Attempted", lng: "Longest Field Goal", xpm: "Extra Points Made", xpa: "Extra Points Attempted" },
		ret: { kr: "Kickoff Returns", krYds: "Kickoff Return Yards", krTD: "Kickoffs returned for touchdowns", pr: "Punt Returns", prYds: "Punt Return Yards", prTD: "Punts returned for touchdowns" },
	};
	const tableKind = (t) => (t.has("Completions") ? "pass" : t.has("Rushing Attempts") ? "rush" : t.has("Receptions") ? "recv" : t.has("Solo Tackles") ? "def" : t.has("Field Goals Made") ? "kick" : t.has("Kickoff Returns") ? "ret" : null);
	const readBoxFull = () => {
		const tables = [...document.querySelectorAll("table")];
		const titlesOf = (t) => new Set([...t.querySelectorAll("thead th")].map((th) => th.title));
		const line = tables.find((t) => titlesOf(t).has("Final score"));
		if (!line) return null;
		const teams = [];
		for (const tr of line.querySelectorAll("tbody tr")) {
			const c = [...tr.children].map((x) => x.textContent.trim());
			teams.push({ abbrev: c[0], q: c.slice(1, -1).map((x) => (/^\d+$/.test(x) ? Number(x) : null)), pts: Number(c[c.length - 1]) || 0, pass: [], rush: [], recv: [], def: [], kick: [], ret: [], pssYds: 0, rusYds: 0, pen: 0, penYds: 0, tov: 0 });
		}
		if (teams.length !== 2) return null;
		const ts = tables.find((t) => titlesOf(t).has("Turnovers"));
		if (ts) {
			[...ts.querySelectorAll("tbody tr")].forEach((tr, i) => {
				const t = teams[i];
				if (!t) return;
				const c = [...tr.children].map((x) => x.textContent.trim());
				t.pssYds = Number(c[0]) || 0;
				t.rusYds = Number(c[1]) || 0;
				const pen = (c[2] || "0-0").split("-");
				t.pen = Number(pen[0]) || 0;
				t.penYds = Number(pen[1]) || 0;
				t.tov = Number(c[3]) || 0;
			});
		}
		const seen = {};
		for (const table of tables) {
			const ths = [...table.querySelectorAll("thead tr:last-child th")];
			if (!ths.length || (ths[0].colSpan || 1) !== 2) continue;
			const kind = tableKind(new Set(ths.map((th) => th.title)));
			if (!kind) continue;
			const full = ths[0].textContent.trim();
			let ti = teams.findIndex((t) => teamNames[t.abbrev] && (full === teamNames[t.abbrev] || full.endsWith(" " + teamNames[t.abbrev])));
			if (ti < 0) ti = (seen[kind] || 0) % 2; // tables come in away/home pairs
			seen[kind] = (seen[kind] || 0) + 1;
			const col = {};
			let c = 0;
			for (const th of ths) {
				if (th.title && col[th.title] === undefined) col[th.title] = c;
				c += th.colSpan || 1;
			}
			for (const tr of table.querySelectorAll("tbody tr")) {
				const a = tr.querySelector('a[href*="/player/"]');
				if (!a) continue;
				const tds = tr.children;
				const row = { name: a.textContent.trim(), pos: tds[0] ? tds[0].textContent.trim() : "", team: teams[ti].abbrev };
				for (const [f, title] of Object.entries(FIELDS[kind])) row[f] = col[title] !== undefined && tds[col[title]] ? Number(tds[col[title]].textContent) || 0 : 0;
				teams[ti][kind].push(row);
			}
		}
		return { teams };
	};

	// ---- what happened, from the play-by-play
	const scanPlays = (container) => {
		const P = { teams: [], score: {}, half: null, scoring: [], big: [], tos: [], sacks: [], injuries: [], missedFG: [], downs: [], leadChanges: 0, maxLead: {}, ot: false };
		let q = 1;
		let off = null;
		let lastQB = null;
		let fumble = null;
		let leader = null;
		const opp = (t) => P.teams.find((x) => x !== t);
		for (const el of [...container.children].reverse()) {
			const r = readEntry(el);
			if (!r) continue;
			if (r.t && !P.teams.includes(r.t)) P.teams.push(r.t);
			if (r.header) off = r.t;
			const s = stripStats(r.orig || "");
			let m;
			if ((m = /^Start of (\d)(?:st|nd|rd|th) quarter$/.exec(s))) {
				q = Number(m[1]);
				if (q === 3 && !P.half) P.half = { ...P.score };
			}
			if (/^Start of .*overtime$/.test(s)) {
				q = 5;
				P.ot = true;
			}
			if ((m = /^(.+) drops back to pass$/.exec(s))) lastQB = m[1];
			if ((m = /^(.+) completed a pass to (.+) for (-?\d+) yards?/.exec(s)) && Number(m[3]) >= 25) P.big.push({ kind: "pass", q, team: r.t, qb: m[1], wr: m[2], yds: Number(m[3]), td: /touchdown/.test(s) });
			if ((m = /^(.+) rushed for (-?\d+) yards?/.exec(s)) && Number(m[2]) >= 20) P.big.push({ kind: "run", q, team: r.t, who: m[1], yds: Number(m[2]), td: /touchdown/.test(s) });
			if ((m = /^(.+) returned the (kickoff|punt) (-?\d+) yards?/.exec(s)) && Number(m[3]) >= 40) P.big.push({ kind: "ret", q, team: r.t, who: m[1], what: m[2], yds: Number(m[3]), td: /touchdown/.test(s) });
			if ((m = /^Intercepted by (.+)!$/.exec(s))) P.tos.push({ kind: "int", q, by: m[1], qb: lastQB, lost: off });
			if ((m = /^(.+) returned the interception (-?\d+) yards?/.exec(s))) {
				const to = P.tos[P.tos.length - 1];
				if (to && to.kind === "int") {
					to.yds = Number(m[2]);
					to.td = /touchdown/.test(s);
				}
			}
			if ((m = /^(.+) fumbled the ball! Forced fumble by (.+)$/.exec(s))) fumble = { who: m[1], by: m[2] };
			if ((m = /^Turnover! (.+) recovered the fumble/.exec(s))) {
				P.tos.push({ kind: "fum", q, rec: m[1], who: fumble && fumble.who, by: fumble && fumble.by, lost: off, td: /touchdown/.test(s) });
				fumble = null;
			}
			if ((m = /^(.+) was sacked by (.+) for/.exec(s))) P.sacks.push({ q, qb: m[1], by: m[2], team: off ? opp(off) : null });
			if ((m = /^(.+) missed a (\d+) yard field goal/.exec(s))) P.missedFG.push({ q, who: m[1], yds: Number(m[2]), team: r.t });
			if (s === "Turnover on downs") P.downs.push({ q, team: off });
			if ((m = /^([A-Z]{1,2}) (.+) was injured!$/.exec(s))) P.injuries.push({ q, pos: m[1], name: m[2], team: r.t });
			const scorer = r.score && r.t ? (/safety/i.test(s) ? opp(r.t) : r.t) : null;
			if (scorer) {
				const before = P.score[scorer] || 0;
				P.score[scorer] = r.score.mine;
				const o = opp(scorer);
				if (o) P.score[o] = r.score.theirs;
				const pts = r.score.mine - before;
				let item = null;
				if ((m = /^(.+) completed a pass to (.+) for (-?\d+) yards? and a touchdown/.exec(s))) item = { kind: "passTD", qb: m[1], wr: m[2], yds: Number(m[3]) };
				else if ((m = /^(.+) rushed for (-?\d+) yards? and a touchdown/.exec(s))) item = { kind: "rushTD", who: m[1], yds: Number(m[2]) };
				else if ((m = /^(.+) returned the interception (-?\d+) yards? for a touchdown/.exec(s))) item = { kind: "intTD", who: m[1], yds: Number(m[2]) };
				else if ((m = /^(.+) returned the (kickoff|punt) (-?\d+) yards? for a touchdown/.exec(s))) item = { kind: "retTD", who: m[1], what: m[2], yds: Number(m[3]) };
				else if ((m = /^(?:Turnover! )?(.+) recovered the fumble.*touchdown/.exec(s))) item = { kind: "fumTD", who: m[1] };
				else if ((m = /^(.+) made a (\d+) yard field goal/.exec(s))) item = { kind: "fg", who: m[1], yds: Number(m[2]) };
				else if (/safety/i.test(s)) item = { kind: "safety" };
				else if (pts >= 6) item = { kind: "td" };
				if (item) P.scoring.push({ ...item, q, team: scorer, pts });
				const a = P.teams[0];
				const b = P.teams[1];
				const sa = P.score[a] || 0;
				const sb = P.score[b] || 0;
				const now = sa === sb ? null : sa > sb ? a : b;
				if (now && leader && now !== leader) P.leadChanges += 1;
				if (now) {
					leader = now;
					P.maxLead[now] = Math.max(P.maxLead[now] || 0, Math.abs(sa - sb));
				}
			}
		}
		return P;
	};

	// ---- league info that doesn't spoil anything
	const leagueInfo = async (abbrevs, mode) => {
		const code = `
const { g, idb, PHASE } = bbgm;
const season = g.get("season");
const A = ${JSON.stringify(abbrevs)};
const half = ${JSON.stringify(mode === "half")};
const teams = (await idb.cache.teams.getAll()).filter((t) => !t.disabled);
const byTid = new Map(teams.map((t) => [t.tid, t]));
const ab = (tid) => (byTid.get(tid) || {}).abbrev;
const tids = A.map((a) => (teams.find((t) => t.abbrev === a) || {}).tid);
const games = await idb.getCopies.games({ season }, "noCopyCache");
const gidMap = new Map(games.map((gm) => [gm.gid, gm]));
let live = null;
for (const gm of games) if (tids.every((tid) => gm.teams.some((t) => t.tid === tid)) && (!live || gm.day > live.day)) live = gm;
let W = null;
try { W = live ? await (${pgmWeekFn.toString()})({ day: live.day }) : null; } catch (e) { W = null; }
const ourG = W && live ? W.games.find((x) => x.gid === live.gid) : null;
const ourSlot = ourG ? ourG.slot : null;
// games already in the books but that "haven't happened yet" from where this show sits
const hidden = new Set();
if (live) {
	if (half) hidden.add(live.gid);
	if (ourSlot !== null) for (const x of W.games) if (x.played && x.gid !== live.gid && (half ? x.slot >= ourSlot : x.slot > ourSlot)) hidden.add(x.gid);
}
const rec = {};
for (const ts of await idb.cache.teamSeasons.getAll()) if (ts.season === season) rec[ts.tid] = [ts.won, ts.lost, ts.tied || 0];
for (const gid of hidden) {
	const gm = gidMap.get(gid);
	if (!gm) continue;
	const [x, y] = gm.teams;
	const undo = (t, o) => { const r = rec[t.tid]; if (r) r[t.pts > o.pts ? 0 : t.pts < o.pts ? 1 : 2] -= 1; };
	undo(x, y); undo(y, x);
}
const out = { recs: {}, upcoming: [], finals: [], divs: [], leaders: {}, windows: null, slot: null, slots: null };
for (const t of teams) out.recs[t.abbrev] = rec[t.tid] || [0, 0, 0];
let ovrOf = null;
try {
	const playoffs = g.get("phase") === PHASE.PLAYOFFS;
	const cacheOvr = new Map();
	ovrOf = async (tid) => {
		if (cacheOvr.has(tid)) return cacheOvr.get(tid);
		const raw = await idb.cache.players.indexGetAll("playersByTid", tid);
		const ps = await idb.getCopies.playersPlus(raw, { attrs: ["injury", "pid", "value", "tid"], ratings: ["ovr", "pos", "ovrs"], season, fuzz: true });
		const t = byTid.get(tid);
		const pti = t && t.playThroughInjuries ? t.playThroughInjuries[playoffs ? 1 : 0] : 0;
		const v = bbgm.team.ovr(ps, { accountForInjuredPlayers: { numDaysInFuture: 0, playThroughInjuries: pti }, playoffs });
		cacheOvr.set(tid, v);
		return v;
	};
} catch (e) {}
const spreadOf = async (home, away) => {
	try {
		if (!ovrOf) return null;
		let sp = 0.3 * ((await ovrOf(home)) - (await ovrOf(away))) + 3 * g.get("homeCourtAdvantage");
		sp *= (g.get("numPeriods") * g.get("quarterLength")) / 60;
		return Math.round(sp * 2) / 2;
	} catch (e) { return null; }
};
const day = live ? live.day : null;
if (ourSlot !== null) {
	out.slot = { idx: ourSlot, ...W.slots[ourSlot] };
	out.slots = W.slots;
	out.windows = [];
	for (const x of W.games) {
		if (x.gid === live.gid) continue;
		const item = { away: ab(x.away), home: ab(x.home), slot: x.slot };
		if (x.played && !hidden.has(x.gid)) Object.assign(item, { state: "final", ap: x.ap, hp: x.hp, ot: x.ot });
		else if (x.played && half && x.slot === ourSlot) Object.assign(item, { state: "half", ap: (x.aq[0] || 0) + (x.aq[1] || 0), hp: (x.hq[0] || 0) + (x.hq[1] || 0) });
		else Object.assign(item, { state: "upcoming", spread: await spreadOf(x.home, x.away) });
		out.windows.push(item);
	}
} else if (day !== null) {
	for (const gm of games) if (gm.day === day && gm !== live && !hidden.has(gm.gid)) out.finals.push({ away: ab(gm.teams[1].tid), home: ab(gm.teams[0].tid), ap: gm.teams[1].pts, hp: gm.teams[0].pts });
	const sched = (await idb.cache.schedule.getAll()).filter((s) => s.day === day && s.homeTid >= 0 && s.awayTid >= 0);
	for (const s of sched) out.upcoming.push({ away: ab(s.awayTid), home: ab(s.homeTid), spread: await spreadOf(s.homeTid, s.awayTid) });
}
const divs = g.get("divs");
for (const tid of tids) {
	const t = byTid.get(tid);
	if (!t || out.divs.some((d) => d.did === t.did)) continue;
	const div = divs.find((d) => d.did === t.did);
	const rows = teams.filter((x) => x.did === t.did).map((x) => ({ abbrev: x.abbrev, r: rec[x.tid] || [0, 0, 0] }));
	rows.sort((a, b) => (b.r[0] + b.r[2] / 2) / Math.max(1, b.r[0] + b.r[1] + b.r[2]) - (a.r[0] + a.r[2] / 2) / Math.max(1, a.r[0] + a.r[1] + a.r[2]) || b.r[0] - a.r[0]);
	const conf = div ? (g.get("confs") || []).find((c) => c.cid === div.cid) : null;
	// "East" alone is ambiguous when both conferences have one: say "American East" (or "AFC East" if that's what the conference is called)
	const unique = div && divs.filter((d) => d.name === div.name).length === 1;
	const cn = conf ? conf.name.split(" ").filter(Boolean)[0] : "";
	out.divs.push({ did: t.did, name: div ? (unique || !cn || div.name.includes(cn) ? div.name : cn + " " + div.name) : "division", rows });
}
const KEYS = ["pssYds", "pssTD", "rusYds", "rusTD", "recYds", "recTD", "defSk", "defInt"];
const tot = new Map();
let counted = 0;
for (const gm of games) {
	if (hidden.has(gm.gid)) continue;
	counted++;
	for (const t of gm.teams) for (const p of t.players || []) {
		let o = tot.get(p.pid);
		if (!o) { o = { pid: p.pid, name: p.name, tid: t.tid }; for (const k of KEYS) o[k] = 0; tot.set(p.pid, o); }
		o.tid = t.tid;
		for (const k of KEYS) o[k] += typeof p[k] === "number" ? p[k] : 0;
	}
}
for (const k of ["pssYds", "rusYds", "recYds", "defSk", "defInt"]) {
	let best = null;
	for (const o of tot.values()) if (o[k] > 0 && (!best || o[k] > best[k])) best = o;
	if (best) {
		let name = best.name;
		if (!name) { const p = await idb.cache.players.get(best.pid); name = p ? p.firstName + " " + p.lastName : "?"; }
		out.leaders[k] = { name, abbrev: ab(best.tid), val: best[k] };
	}
}
out.games = counted;
console.log(JSON.stringify(out));`;
		return JSON.parse(await window.bbgm.toWorker("main", "evalOnWorker", code));
	};

	// ---- building the scripts
	const qbOf = (T) => T.pass.slice().sort((a, b) => b.att - a.att)[0];
	const qbLine = (q) => `${q.cmp} of ${q.att} for ${q.yds} yards${q.td ? `, ${plural(q.td, "touchdown", "touchdowns")}` : ""}${q.int ? `, ${plural(q.int, "pick", "picks")}` : ""}`;
	const totYds = (T) => T.pssYds + T.rusYds;
	const defScore = (d) => d.int * 6 + d.intTD * 6 + d.frTD * 6 + d.sk * 4 + d.ff * 4 + d.fr * 3 + d.pd * 1.5 + d.tck * 0.8 + d.tfl;
	const defLine = (d) => {
		const bits = [];
		if (d.tck) bits.push(plural(d.tck, "tackle", "tackles"));
		if (d.sk) bits.push(plural(d.sk, "sack", "sacks"));
		if (d.int) bits.push(plural(d.int, "interception", "interceptions"));
		if (d.pd) bits.push(plural(d.pd, "pass breakup", "pass breakups"));
		if (d.ff) bits.push(plural(d.ff, "forced fumble", "forced fumbles"));
		if (d.intTD || d.frTD) bits.push("a defensive touchdown");
		return listAnd(bits);
	};
	const bestOffense = (T) => {
		const c = [];
		const q = qbOf(T);
		if (q && q.att > 0) c.push({ score: q.yds / 2 + q.td * 15 - q.int * 10, txt: `${last(q.name)} has thrown for ${q.yds} yards${q.td ? ` and ${plural(q.td, "touchdown", "touchdowns")}` : ""}`, name: q.name });
		for (const r of T.rush) c.push({ score: r.yds + r.td * 15, txt: `${last(r.name)} has ${r.yds} yards on ${plural(r.att, "carry", "carries")}${r.td ? `, ${plural(r.td, "score", "scores")}` : ""}`, name: r.name });
		for (const r of T.recv) c.push({ score: r.yds + r.td * 15, txt: `${last(r.name)} has ${plural(r.rec, "catch", "catches")} for ${r.yds} yards${r.td ? ` and ${plural(r.td, "touchdown", "touchdowns")}` : ""}`, name: r.name });
		return c.sort((a, b) => b.score - a.score)[0] || null;
	};
	const scoreBit = (s) => {
		if (s.kind === "passTD") return `${last(s.qb)} to ${last(s.wr)} from ${s.yds}`;
		if (s.kind === "rushTD") return `${last(s.who)} on a ${s.yds}-yard run`;
		if (s.kind === "intTD") return `${last(s.who)}'s ${s.yds}-yard pick-six`;
		if (s.kind === "retTD") return `${last(s.who)}'s ${s.yds}-yard ${s.what} return`;
		if (s.kind === "fumTD") return `${last(s.who)}'s fumble return`;
		if (s.kind === "fg") return `a ${s.yds}-yarder from ${last(s.who)}`;
		if (s.kind === "safety") return "a safety";
		return "a touchdown";
	};
	// the one play everyone will be talking about
	// the one play everyone will be talking about (after a win, one of the winner's plays if there's a good one)
	const playOf = (P, inRange, team) => {
		const pick = (mine) => {
			const ok = (x) => !mine || x.team === team;
			const sc = P.scoring.filter((s) => inRange(s.q) && ok(s));
			const special = sc.filter((s) => s.kind === "intTD" || s.kind === "fumTD" || s.kind === "retTD").sort((a, b) => (b.yds || 0) - (a.yds || 0))[0];
			if (special) return { type: special.kind, s: special };
			const longTD = sc.filter((s) => (s.kind === "passTD" || s.kind === "rushTD") && s.yds >= 30).sort((a, b) => b.yds - a.yds)[0];
			if (longTD) return { type: longTD.kind, s: longTD };
			const big = P.big.filter((b) => inRange(b.q) && ok(b)).sort((a, b) => b.yds - a.yds)[0];
			if (big && big.yds >= 35) return { type: "big", s: big };
			const to = P.tos.filter((t) => inRange(t.q) && (!mine || t.lost !== team))[0];
			if (to) return { type: to.kind, s: to };
			return null;
		};
		return (team && pick(true)) || pick(false);
	};
	const playTalk = (pl, p, when) => {
		if (!pl) return null;
		const s = pl.s;
		if (pl.type === "intTD") return p([`The play of the ${when} has to be ${s.who}. He reads it the whole way and takes it ${s.yds} yards to the house. That changes everything.`, `Give me ${last(s.who)}'s pick-six. Undercuts the route, ${s.yds} yards the other way. That's film study paying off.`]);
		if (pl.type === "retTD") return p([`${s.who} took that ${s.what} back ${s.yds} yards. Special teams just flipped this game.`, `The ${s.what} return by ${last(s.who)}. ${s.yds} yards, and the coverage unit never laid a finger on him.`]);
		if (pl.type === "fumTD") return `${s.who} scooping it up and taking it in. That's a gift, and they cashed it.`;
		if (pl.type === "passTD") return p([`${last(s.wr)} got behind the defense and ${last(s.qb)} put it right on him for ${s.yds}. Somebody blew a coverage there.`, `The ${s.yds}-yard strike from ${last(s.qb)} to ${last(s.wr)}. That's the play of the ${when}, no question.`]);
		if (pl.type === "rushTD") return p([`${s.who} on that ${s.yds}-yard run. He hit the hole and was gone.`, `That ${s.yds}-yard touchdown run by ${last(s.who)}. The line opened a lane you could drive a truck through.`]);
		if (pl.type === "big") {
			if (s.kind === "pass") return `${last(s.qb)} to ${last(s.wr)} for ${s.yds}. That's the kind of chunk play that flips field position.`;
			if (s.kind === "run") return `${last(s.who)}'s ${s.yds}-yard run. He found the crease and made a man miss.`;
			return `${last(s.who)}'s ${s.yds}-yard ${s.what} return set up great field position.`;
		}
		if (pl.type === "int") return `The turning point was ${last(s.by)}'s interception.${s.qb ? ` ${last(s.qb)} tried to force that one.` : ""}`;
		if (pl.type === "fum") return `${s.by ? `${last(s.by)} punched that ball out` : "That fumble"}${s.rec ? ` and ${last(s.rec)} fell on it` : ""}. Momentum swing right there.`;
		return null;
	};
	const keyStats = (B, P, lead, phrase) => {
		const [A, H] = B.teams;
		const out = [];
		if (A.tov !== H.tov) {
			const good = A.tov < H.tov ? A : H;
			const bad = good === A ? H : A;
			out.push(`The ${nick(good.abbrev)} have won the turnover battle, ${plural(bad.tov, "giveaway", "giveaways")} to ${good.tov}.${lead && good === lead ? ` That's been the difference ${phrase}.` : lead ? phrase === "today" ? " And they still lost." : " And they're still behind." : ""}`);
		}
		const ya = totYds(A);
		const yh = totYds(H);
		if (Math.abs(ya - yh) >= 90) {
			const more = ya > yh ? A : H;
			const less = more === A ? H : A;
			out.push(`The ${nick(more.abbrev)} have out-gained the ${nick(less.abbrev)} ${totYds(more)} to ${totYds(less)}${lead && more !== lead ? ", and they're still behind. That tells you about the mistakes" : ""}.`);
		}
		for (const T of B.teams) {
			const sk = P.sacks.filter((s) => s.team === T.abbrev);
			if (sk.length >= 3) {
				const by = {};
				for (const s of sk) by[s.by] = (by[s.by] || 0) + 1;
				const top = Object.entries(by).sort((a, b) => b[1] - a[1])[0];
				out.push(`The ${nick(T.abbrev)} pass rush has ${sk.length} sacks${top && top[1] >= 2 ? `, ${top[1]} of them from ${last(top[0])}` : ""}.`);
			}
		}
		for (const T of B.teams) if (T.pen >= 6) out.push(`The ${nick(T.abbrev)} have been flagged ${T.pen} times for ${T.penYds} yards. You can't beat yourself like that.`);
		for (const T of B.teams) if (T.rusYds < 30 && totYds(T) > 0) out.push(`Just ${T.rusYds} rushing yards for the ${nick(T.abbrev)}. They've been one-dimensional.`);
		return out;
	};
	const injuryTalk = (P, B) => {
		if (!P.injuries.length) return null;
		const bits = P.injuries.map((i) => `${i.pos} ${i.name}${i.team ? ` (${nick(i.team)})` : ""}`);
		return `Injury update: ${listAnd(bits)} ${P.injuries.length === 1 ? "went down" : "have gone down"} today. We'll pass along anything we hear.`;
	};
	const studio = (L, B, mode) => {
		if (!L) return [];
		const lines = [];
		const going = mode === "half" ? ", as it stands" : "";
		lines.push(mode === "half" ? "Thanks, Rick. Let's take a look around the league." : "Thanks, guys. Let's check in around the league.");
		if (L.windows && L.slot) {
			const our = L.slot.idx;
			const sunday = L.slot.key === "SUN11" || L.slot.key === "SUN1";
			const IN = { TNF: "On Thursday night", SUN11: "In the 11:00 window", SUN1: "In the 1:00 window", SNF: "On Sunday night", MNF: "On Monday night" };
			const OF = { TNF: "Thursday night", SUN11: "the 11:00 window", SUN1: "the 1:00 window", SNF: "Sunday night", MNF: "Monday night" };
			const gameStr = (x) => (x.hp >= x.ap ? `${nick(x.home)} ${x.hp}, ${nick(x.away)} ${x.ap}` : `${nick(x.away)} ${x.ap}, ${nick(x.home)} ${x.hp}`);
			const beatStr = (x) => (x.hp === x.ap ? `the ${nick(x.away)} and ${nick(x.home)} tied at ${x.hp}` : x.hp > x.ap ? `the ${nick(x.home)} beat the ${nick(x.away)} ${x.hp}-${x.ap}` : `the ${nick(x.away)} beat the ${nick(x.home)} ${x.ap}-${x.hp}`);
			const lineStr = (u) => {
				const sp = u.spread === null || u.spread === undefined ? "" : u.spread === 0 ? ", a pick'em" : u.spread > 0 ? `, ${nick(u.home)} by ${Math.abs(u.spread)}` : `, ${nick(u.away)} by ${Math.abs(u.spread)}`;
				return `the ${nick(u.away)} (${recStr(L.recs[u.away])}) at the ${nick(u.home)} (${recStr(L.recs[u.home])})${sp}`;
			};
			const groups = (pred) => {
				const m = new Map();
				for (const w of L.windows.filter(pred)) {
					if (!m.has(w.slot)) m.set(w.slot, []);
					m.get(w.slot).push(w);
				}
				return [...m.entries()].sort((a, b) => a[0] - b[0]);
			};
			for (const [slot, ws] of groups((w) => w.state === "final" && w.slot < our)) {
				const key = L.slots[slot].key;
				if (ws.length === 1) lines.push(`${IN[key]}, ${beatStr(ws[0])}.`);
				else lines.push(`${IN[key]}: ${ws.slice(0, 5).map(gameStr).join("; ")}${ws.length > 5 ? `, and ${ws.length - 5} more` : ""}.`);
			}
			const same = L.windows.filter((w) => w.slot === our && (w.state === "half" || w.state === "final"));
			if (same.length) lines.push(mode === "half" ? `Elsewhere in ${OF[L.slot.key]} at the half: ${same.map(gameStr).join("; ")}.` : `Final scores from ${OF[L.slot.key]}: ${same.map(gameStr).join("; ")}.`);
			const pct = (a) => {
				const r = L.recs[a] || [0, 0, 0];
				return (r[0] + r[2] / 2) / Math.max(1, r[0] + r[1] + r[2]);
			};
			const later = [];
			for (const [slot, ws] of groups((w) => w.state === "upcoming")) {
				const key = L.slots[slot].key;
				const when = key === "SNF" && sunday ? "tonight on Sunday Night Football" : key === "SNF" ? "Sunday night" : key === "MNF" ? "Monday night" : key === "TNF" ? "Thursday night" : `the ${L.slots[slot].time.replace(" AM", "").replace(" PM", "")} window`;
				if (ws.length === 1) later.push(`${when}, ${lineStr(ws[0])}`);
				else {
					const top = ws.slice().sort((a, b) => pct(b.away) + pct(b.home) - pct(a.away) - pct(a.home))[0];
					later.push(`${plural(ws.length, "game", "games")} in ${when}, led by ${lineStr(top)}`);
				}
			}
			if (later.length) lines.push(`Still to come: ${later.join("; ")}.`);
		} else if (L.finals.length) lines.push(`Already final this week: ${listAnd(L.finals.slice(0, 5).map((f) => (f.hp >= f.ap ? `${nick(f.home)} ${f.hp}, ${nick(f.away)} ${f.ap}` : `${nick(f.away)} ${f.ap}, ${nick(f.home)} ${f.hp}`)))}.`);
		if (!L.windows && L.upcoming.length) {
			const mine = new Set(B.teams.map((t) => t.abbrev));
			const divTeams = new Set(L.divs.flatMap((d) => d.rows.map((r) => r.abbrev)));
			const pct = (a) => {
				const r = L.recs[a] || [0, 0, 0];
				return (r[0] + r[2] / 2) / Math.max(1, r[0] + r[1] + r[2]);
			};
			const ranked = L.upcoming.filter((u) => !mine.has(u.away) && !mine.has(u.home)).map((u) => ({ ...u, w: (divTeams.has(u.away) || divTeams.has(u.home) ? 2 : 0) + pct(u.away) + pct(u.home) })).sort((a, b) => b.w - a.w);
			const pick = ranked.slice(0, 4);
			const say = (u) => {
				const line = u.spread === null || u.spread === undefined ? "" : u.spread === 0 ? ", a pick'em" : u.spread > 0 ? `, ${nick(u.home)} by ${Math.abs(u.spread)}` : `, ${nick(u.away)} by ${Math.abs(u.spread)}`;
				return `${nick(u.away)} (${recStr(L.recs[u.away])}) at ${nick(u.home)} (${recStr(L.recs[u.home])})${line}`;
			};
			if (pick.length) lines.push(`Still to come this week: ${pick.map(say).join("; ")}${ranked.length > pick.length ? `, plus ${plural(ranked.length - pick.length, "more game", "more games")}` : ""}.`);
		}
		for (const d of L.divs) lines.push(`In the ${d.name}${going}: ${d.rows.map((r) => `${nick(r.abbrev)} ${recStr(r.r)}`).join(", ")}.`);
		const ld = L.leaders;
		const lb = [];
		if (ld.pssYds) lb.push(`${ld.pssYds.name} (${ld.pssYds.abbrev}) leads the league with ${ld.pssYds.val.toLocaleString()} passing yards`);
		if (ld.rusYds) lb.push(`${ld.rusYds.name} (${ld.rusYds.abbrev}) tops the rushers at ${ld.rusYds.val.toLocaleString()}`);
		if (ld.recYds) lb.push(`${ld.recYds.name} (${ld.recYds.abbrev}) has a league-best ${ld.recYds.val.toLocaleString()} receiving yards`);
		if (ld.defSk && ld.defSk.val >= 2) lb.push(`and ${ld.defSk.name} (${ld.defSk.abbrev}) leads with ${ld.defSk.val} sacks`);
		if (lb.length && L.games > 0) lines.push(`${mode === "half" ? "League leaders coming into today" : "League leaders after today"}: ${lb.join("; ")}.`);
		lines.push(mode === "half" ? "Back to you, Rick." : "That's going to do it for us. For Rick and Deke, I'm Monica. Thanks for watching.");
		return lines;
	};
	const strip = (B, upToQ) => B.teams.map((T) => ({ abbrev: T.abbrev, q: T.q.slice(0, upToQ ? upToQ : T.q.length), pts: T.pts, yds: totYds(T), tov: T.tov }));

	const buildHalftime = (B, P, L) => {
		const [A, H] = B.teams;
		const p = picker(`half|${A.abbrev}|${H.abbrev}|${A.pts}-${H.pts}|${totYds(A)}`);
		const lines = [];
		const say = (who, text) => text && lines.push({ who, text });
		const seg = (t) => lines.push({ seg: t });
		const lead = A.pts === H.pts ? null : A.pts > H.pts ? A : H;
		const trail = lead ? (lead === A ? H : A) : null;
		const diff = Math.abs(A.pts - H.pts);
		const N = (T) => nick(T.abbrev);
		seg("The first half");
		if (!lead && A.pts === 0) say("RICK", p([`Welcome back, everybody. It's halftime, and nobody's found the end zone yet. Scoreless between the ${N(A)} and the ${N(H)}.`, "Halftime, and the defenses own this one so far. Still 0-0."]));
		else if (!lead) say("RICK", p([`All square at the break, ${A.pts} apiece. The ${N(A)} and ${N(H)} have traded punches all half.`, `We're tied at ${A.pts} at halftime. Anybody's ballgame.`]));
		else if (diff >= 21) say("RICK", p([`Halftime, and this one's gotten away from the ${N(trail)}. ${N(lead)} ${lead.pts}, ${N(trail)} ${trail.pts}.`, `It's been all ${N(lead)} so far. They lead ${lead.pts} to ${trail.pts} at the break.`]));
		else if (diff >= 9) say("RICK", p([`Welcome back. The ${N(lead)} take a ${diff}-point lead into the locker room, ${lead.pts} to ${trail.pts}.`, `Halftime here, and the ${N(lead)} are up ${lead.pts}-${trail.pts}. A two-score cushion.`]));
		else say("RICK", p([`One-score game at the half. ${N(lead)} ${lead.pts}, ${N(trail)} ${trail.pts}.`, `The ${N(lead)} clinging to a ${diff}-point lead at the break, ${lead.pts} to ${trail.pts}.`]));
		if (L && L.slot && ["TNF", "SNF", "MNF"].includes(L.slot.key) && lines[1] && lines[1].who === "RICK") lines[1].text = `Welcome back to ${L.slot.name}. ` + lines[1].text.replace(/^Welcome back(, everybody)?\. /, "");
		if (P.leadChanges >= 2) say("RICK", `We've already had ${P.leadChanges} lead changes.`);

		const focus = lead || (totYds(A) >= totYds(H) ? A : H);
		const q = qbOf(focus);
		if (q && q.att >= 5) {
			const pct = q.cmp / q.att;
			const adj = q.int >= 2 && q.int >= q.td ? "careless with the football" : q.td >= 3 && pct >= 0.6 ? p(["on fire", "dealing", "in a groove"]) : q.td >= 2 && q.int === 0 && pct >= 0.6 ? p(["surgical", "dialed in", "sharp"]) : pct >= 0.7 && q.int <= 1 ? p(["efficient", "sharp"]) : pct < 0.5 ? "up and down" : "steady";
			const sk = q.sk >= 3 ? ` And he's been sacked ${q.sk} times, so he's earned every one of those yards.` : "";
			say("DEKE", `${p([`Rick, ${last(q.name)} has been ${adj}`, `${q.name} has been ${adj}`])}: ${qbLine(q)}.${sk}`);
		}
		const rb = focus.rush.slice().sort((a, b) => b.yds - a.yds)[0];
		if (rb && (rb.yds >= 60 || rb.td >= 2)) say("DEKE", `And ${last(rb.name)} has been the engine on the ground: ${rb.yds} yards on ${plural(rb.att, "carry", "carries")}${rb.td ? `, ${plural(rb.td, "touchdown", "touchdowns")}` : ""}.`);
		const byTeam = B.teams.map((T) => ({ T, s: P.scoring.filter((s) => s.team === T.abbrev && s.q <= 2) })).filter((x) => x.s.length);
		if (lead) byTeam.sort((a, b) => (b.T === lead) - (a.T === lead));
		if (byTeam.length === 1) say("RICK", `All the scoring so far belongs to the ${N(byTeam[0].T)}: ${listAnd(byTeam[0].s.map(scoreBit))}.`);
		else if (byTeam.length === 2) say("RICK", `Scoring for the ${N(byTeam[0].T)}: ${listAnd(byTeam[0].s.map(scoreBit))}. The ${N(byTeam[1].T)} have answered with ${listAnd(byTeam[1].s.map(scoreBit))}.`);

		const pl = playOf(P, (qq) => qq <= 2);
		const talk = playTalk(pl, p, "half");
		if (talk) {
			seg("Play of the half");
			say("DEKE", talk);
		}

		seg("Inside the numbers");
		if (trail) {
			const best = bestOffense(trail);
			if (diff >= 21) say("RICK", `Not much going right for the ${N(trail)}: ${totYds(trail)} total yards and ${plural(trail.tov, "turnover", "turnovers")}.`);
			else if (best) say("RICK", `${p([`The ${N(trail)} aren't out of this.`, `Don't count out the ${N(trail)}.`])} ${best.txt}.`);
		} else {
			const bests = B.teams.map(bestOffense).filter(Boolean);
			if (bests.length) say("RICK", `${listAnd(bests.map((b) => b.txt))}.`);
		}
		const ks = keyStats(B, P, lead, "so far");
		for (const k of ks.slice(0, 2)) say("DEKE", k);
		const defs = B.teams.flatMap((T) => T.def).sort((a, b) => defScore(b) - defScore(a));
		if (defs[0] && defScore(defs[0]) >= 4) say("RICK", `${p(["Defensive standout so far", "Defensive player of the half"])}: ${defs[0].pos} ${defs[0].name} of the ${nick(defs[0].team)}. ${cap(defLine(defs[0]))}.`);
		const inj = injuryTalk(P, B);
		if (inj) {
			seg("Injury report");
			say("RICK", inj);
		}
		const st = studio(L, B, "half");
		if (st.length) {
			seg("Around the league");
			for (const s of st) say("MONICA", s);
		}
		seg("Second half");
		if (trail) {
			const tips = [];
			if (trail.tov >= 2) tips.push("take care of the football");
			if (trail.rusYds < 40) tips.push("get the run game going");
			const skd = trail.pass.reduce((a, x) => a + x.sk, 0);
			if (skd >= 3) tips.push("get the ball out quicker");
			if (P.big.filter((b) => b.team === lead.abbrev && b.q <= 2).length >= 2) tips.push("stop giving up the big play");
			if (!tips.length) tips.push("get a stop on the first series");
			say("DEKE", `If I'm the ${N(trail)}, I want to ${listAnd(tips.slice(0, 2))}. ${diff >= 17 ? "They need points on just about every possession now." : "There's plenty of time."}`);
		} else say("DEKE", "Whoever wins the turnover battle in the second half wins this game.");
		say("RICK", p(["Second half coming up. Stick with us.", "We'll be right back with the third quarter.", "Don't go anywhere. The second half is next."]));
		return { kind: "half", title: `Halftime · ${N(A)} ${A.pts}, ${N(H)} ${H.pts}`, lines, strip: strip(B, 2) };
	};

	const buildPostgame = (B, P, L) => {
		const [A, H] = B.teams;
		const p = picker(`post|${A.abbrev}|${H.abbrev}|${A.pts}-${H.pts}|${totYds(A)}`);
		const lines = [];
		const say = (who, text) => text && lines.push({ who, text });
		const seg = (t) => lines.push({ seg: t });
		const N = (T) => nick(T.abbrev);
		const W = A.pts === H.pts ? null : A.pts > H.pts ? A : H;
		const Lz = W ? (W === A ? H : A) : null;
		const m = Math.abs(A.pts - H.pts);
		seg("Final");
		const half = P.half;
		const hd = half && W ? (half[Lz.abbrev] || 0) - (half[W.abbrev] || 0) : 0;
		if (!W) say("RICK", `It ends in a tie, ${A.pts}-${H.pts}. Nobody goes home happy.`);
		else if (hd > 0) say("RICK", p([`What a comeback! The ${N(W)} were down ${hd} at the half and win it ${W.pts}-${Lz.pts}.`, `They were down ${hd} at halftime, and the ${N(W)} storm back to win ${W.pts}-${Lz.pts}!`]));
		else if (P.ot) say("RICK", `They needed overtime, but the ${N(W)} get it done, ${W.pts}-${Lz.pts}.`);
		else if (m >= 21) say("RICK", p([`That's a wrap. The ${N(W)} roll, ${W.pts}-${Lz.pts}.`, `Total domination. ${N(W)} ${W.pts}, ${N(Lz)} ${Lz.pts}.`]));
		else if (m <= 3) say("RICK", p([`What a finish! The ${N(W)} hang on, ${W.pts}-${Lz.pts}.`, `A nail-biter to the end, and the ${N(W)} survive, ${W.pts}-${Lz.pts}.`]));
		else say("RICK", p([`Final here: ${N(W)} ${W.pts}, ${N(Lz)} ${Lz.pts}.`, `That's the ballgame. The ${N(W)} win it ${W.pts}-${Lz.pts}.`]));
		if (half) {
			const s2 = B.teams.map((T) => T.pts - (half[T.abbrev] || 0));
			if (s2[0] !== s2[1] && Math.abs(s2[0] - s2[1]) >= 10) {
				const i = s2[0] > s2[1] ? 0 : 1;
				say("RICK", `The ${N(B.teams[i])} won the second half ${s2[i]}-${s2[1 - i]}.`);
			}
		}

		// player of the game
		const imp = new Map();
		const add = (T, row, v, kind) => {
			const k = `${T.abbrev}|${row.name}`;
			const o = imp.get(k) || { name: row.name, pos: row.pos, team: T.abbrev, v: 0, rows: {} };
			o.v += v;
			o.rows[kind] = row;
			imp.set(k, o);
		};
		for (const T of B.teams) {
			for (const r of T.pass) add(T, r, r.yds / 20 + r.td * 4 - r.int * 3, "pass");
			for (const r of T.rush) add(T, r, r.yds / 10 + r.td * 6, "rush");
			for (const r of T.recv) add(T, r, r.yds / 10 + r.td * 6 + r.rec * 0.3, "recv");
			for (const r of T.def) add(T, r, defScore(r), "def");
			for (const r of T.ret) add(T, r, (r.krYds + r.prYds) / 25 + (r.krTD + r.prTD) * 6, "ret");
			for (const r of T.kick) add(T, r, r.fgm * 3, "kick");
		}
		const all = [...imp.values()].sort((a, b) => b.v - a.v);
		const pog = (W ? all.filter((x) => x.team === W.abbrev) : all)[0];
		const statLine = (o) => {
			const bits = [];
			const r = o.rows;
			if (r.pass && r.pass.att) bits.push(qbLine(r.pass));
			if (r.rush && r.rush.att) bits.push(`${plural(r.rush.att, "carry", "carries")} for ${r.rush.yds} yards${r.rush.td ? ` and ${plural(r.rush.td, "touchdown", "touchdowns")}` : ""}`);
			if (r.recv && r.recv.rec) bits.push(`${plural(r.recv.rec, "catch", "catches")} for ${r.recv.yds} yards${r.recv.td ? ` and ${plural(r.recv.td, "touchdown", "touchdowns")}` : ""}`);
			if (r.def && defScore(r.def) >= 2) bits.push(defLine(r.def));
			if (r.ret && (r.ret.krTD || r.ret.prTD || r.ret.krYds + r.ret.prYds >= 80)) bits.push(`${r.ret.krYds + r.ret.prYds} return yards${r.ret.krTD + r.ret.prTD ? " and a return touchdown" : ""}`);
			if (r.kick && r.kick.fgm) bits.push(`${r.kick.fgm} of ${r.kick.fga} on field goals`);
			return bits.join("; ");
		};
		if (pog) {
			seg("Player of the game");
			say("DEKE", `${p(["Player of the game has to be", "My player of the game:", "Give the game ball to"])} ${pog.pos} ${pog.name}. ${cap(statLine(pog))}.`);
		}
		const pl = playOf(P, () => true, W ? W.abbrev : null);
		const talk = playTalk(pl, p, "game");
		if (talk) {
			seg("Play of the game");
			say("DEKE", talk);
		}
		seg("Inside the numbers");
		if (Lz) {
			const best = bestOffense(Lz);
			if (best && (!pog || best.name !== pog.name)) say("RICK", `For the ${N(Lz)}, ${best.txt} in a losing effort.`);
		}
		for (const k of keyStats(B, P, W, "today").slice(0, 2)) say("DEKE", k);
		const defs = B.teams.flatMap((T) => T.def).sort((a, b) => defScore(b) - defScore(a));
		if (defs[0] && defScore(defs[0]) >= 4 && (!pog || defs[0].name !== pog.name)) say("RICK", `Defensively, ${defs[0].pos} ${defs[0].name} of the ${nick(defs[0].team)} was everywhere: ${defLine(defs[0])}.`);
		const missed = P.missedFG.length ? `${P.missedFG.map((f) => `${last(f.who)} missed from ${f.yds}`).join(", ")}.` : "";
		if (missed && m <= 7) say("DEKE", `And don't forget the kicks: ${missed} In a game this close, those points matter.`);
		const inj = injuryTalk(P, B);
		if (inj) {
			seg("Injury report");
			say("RICK", inj.replace("Injury update: ", "On the injury front: "));
		}
		if (L && W) say("RICK", `The ${N(W)} move to ${recStr(L.recs[W.abbrev])}; the ${N(Lz)} fall to ${recStr(L.recs[Lz.abbrev])}.`);
		else if (L) say("RICK", `The ${N(A)} are now ${recStr(L.recs[A.abbrev])}, the ${N(H)} ${recStr(L.recs[H.abbrev])}.`);
		const st = studio(L, B, "post");
		if (st.length) {
			seg("Around the league");
			for (const s of st) say("MONICA", s);
		}
		return { kind: "post", title: `Final · ${N(A)} ${A.pts}, ${N(H)} ${H.pts}${P.ot ? " (OT)" : ""}`, lines, strip: strip(B) };
	};

	// ---- on screen
	const injectStyle = () => {
		if (document.getElementById("pgm-show-style")) return;
		const st = document.createElement("style");
		st.id = "pgm-show-style";
		st.textContent = `
.pgm-show-bg{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:2050;display:flex;align-items:center;justify-content:center;padding:16px}
.pgm-show{background:var(--bs-body-bg,#fff);color:var(--bs-body-color,#212529);border:1px solid var(--bs-border-color,#dee2e6);border-radius:10px;max-width:760px;width:100%;max-height:88vh;display:flex;flex-direction:column;box-shadow:0 10px 40px rgba(0,0,0,.45)}
.pgm-show-head{padding:12px 16px;border-bottom:1px solid var(--bs-border-color,#dee2e6);display:flex;align-items:center;gap:10px}
.pgm-show-head h4{margin:0;font-size:1.15rem;flex:1}
.pgm-show-body{padding:8px 16px 12px;overflow-y:auto}
.pgm-show-line{margin:0 0 10px;line-height:1.5}
.pgm-show-who{font-weight:700}
.pgm-show-role{font-size:.72em;opacity:.65;margin:0 6px 0 3px;text-transform:uppercase;letter-spacing:.05em}
.pgm-show-seg{font-size:.72em;font-weight:700;text-transform:uppercase;letter-spacing:.09em;opacity:.55;margin:14px 0 6px;border-bottom:1px solid var(--bs-border-color,#dee2e6);padding-bottom:2px}
.pgm-show-foot{padding:10px 16px;border-top:1px solid var(--bs-border-color,#dee2e6);display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap}
.pgm-show-strip{font-size:.85em;margin:8px 0 2px;width:auto}
.pgm-show-strip td,.pgm-show-strip th{padding:2px 8px;text-align:center}
.pgm-show-strip td:first-child,.pgm-show-strip th:first-child{text-align:left}
@keyframes pgmShowIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.pgm-show-line,.pgm-show-seg{animation:pgmShowIn .35s ease-out}`;
		document.head.appendChild(st);
	};
	const clickVisible = (pred) => {
		const b = [...document.querySelectorAll("button")].find((x) => x.offsetParent !== null && pred(x.title || ""));
		if (b) b.click();
		return !!b;
	};
	let openShowEl = null;
	const openShow = (show, pausedByUs) => {
		if (!show) return;
		injectStyle();
		if (openShowEl) openShowEl.remove();
		const bg = document.createElement("div");
		bg.className = "pgm-show-bg";
		const box = document.createElement("div");
		box.className = "pgm-show";
		bg.appendChild(box);
		const qs = Math.max(...show.strip.map((s) => s.q.length));
		const qName = (i) => (i < 4 ? String(i + 1) : i === 4 ? "OT" : `${i - 3}OT`);
		box.innerHTML = `<div class="pgm-show-head"><h4>🎙 ${esc(show.kind === "half" ? "Halftime Show" : "Postgame Show")}</h4><button type="button" class="btn-close" aria-label="Close"></button></div>
<div class="pgm-show-body"><div class="fw-bold">${esc(show.title)}</div>
<table class="table table-sm pgm-show-strip"><thead><tr><th></th>${Array.from({ length: qs }, (_, i) => `<th>${qName(i)}</th>`).join("")}<th>Pts</th><th>Yds</th><th>TOV</th></tr></thead><tbody>${show.strip.map((s) => `<tr><td>${esc(s.abbrev)}</td>${Array.from({ length: qs }, (_, i) => `<td>${s.q[i] ?? "-"}</td>`).join("")}<td class="fw-bold">${show.kind === "half" ? s.q.reduce((a, x) => a + (x || 0), 0) : s.pts}</td><td>${s.yds}</td><td>${s.tov}</td></tr>`).join("")}</tbody></table>
<div class="pgm-show-lines"></div></div>
<div class="pgm-show-foot"><button type="button" class="btn btn-secondary btn-sm pgm-show-skip">Show it all</button><button type="button" class="btn btn-primary btn-sm pgm-show-go">${show.kind === "half" ? "Start the second half ▶" : "Close"}</button></div>`;
		const body = box.querySelector(".pgm-show-body");
		const holder = box.querySelector(".pgm-show-lines");
		const skip = box.querySelector(".pgm-show-skip");
		let i = 0;
		const addLine = () => {
			const l = show.lines[i++];
			if (!l) return false;
			const d = document.createElement("div");
			if (l.seg) {
				d.className = "pgm-show-seg";
				d.textContent = l.seg;
			} else {
				const [name, role, cls] = CAST[l.who];
				d.className = "pgm-show-line";
				d.innerHTML = `<span class="pgm-show-who ${cls}">${esc(name.toUpperCase())}</span><span class="pgm-show-role">${esc(role)}</span>${esc(l.text)}`;
			}
			holder.appendChild(d);
			return true;
		};
		const atBottom = () => body.scrollHeight - body.scrollTop - body.clientHeight < 40;
		let timer = null;
		const tick = () => {
			const follow = atBottom();
			// segment headers come with the line after them
			let more = addLine();
			while (more && show.lines[i - 1].seg) more = addLine();
			if (follow) body.scrollTop = body.scrollHeight;
			if (!more || i >= show.lines.length) {
				skip.style.display = "none";
				clearInterval(timer);
			}
		};
		tick();
		timer = setInterval(tick, 1700);
		skip.addEventListener("click", () => {
			clearInterval(timer);
			while (addLine());
			skip.style.display = "none";
		});
		const close = () => {
			clearInterval(timer);
			bg.remove();
			document.removeEventListener("keydown", onKey);
			if (openShowEl === bg) openShowEl = null;
			if (pausedByUs) clickVisible((t) => t.startsWith("Resume Simulation"));
		};
		const onKey = (e) => {
			if (e.key === "Escape") close();
		};
		document.addEventListener("keydown", onKey);
		box.querySelector(".btn-close").addEventListener("click", close);
		box.querySelector(".pgm-show-go").addEventListener("click", close);
		document.body.appendChild(bg);
		openShowEl = bg;
	};

	const showDone = new WeakSet();
	const maybeShow = (r, isLast, container) => {
		if (!enabled || !r || !r.orig || showDone.has(r.el)) return;
		const s = stripStats(r.orig);
		const kind = s === "Start of 3rd quarter" ? "half" : s === "End of game" ? "post" : null;
		if (!kind) return;
		showDone.add(r.el);
		// pause right away so the 3rd quarter doesn't start under the show
		const pausedByUs = kind === "half" && isLast ? clickVisible((t) => t.startsWith("Pause Simulation")) : false;
		const B = readBoxFull();
		if (!B) return;
		const P = scanPlays(container);
		const ready = leagueInfo(B.teams.map((t) => t.abbrev), kind)
			.catch((e) => {
				console.log("Broadcast Booth (league info): " + e.message);
				return null;
			})
			.then((L) => (kind === "half" ? buildHalftime(B, P, L) : buildPostgame(B, P, L)))
			.catch((e) => {
				console.log("Broadcast Booth (show): " + e.message);
				return null;
			});
		const b = document.createElement("button");
		b.type = "button";
		b.className = "btn btn-sm btn-outline-secondary ms-2 py-0 pgm-show-btn";
		b.textContent = kind === "half" ? "🎙 Halftime show" : "🎙 Postgame show";
		b.addEventListener("click", () => ready.then((sh) => openShow(sh, false)));
		r.body.insertBefore(b, r.scoreDiv);
		if (isLast) ready.then((sh) => (sh ? openShow(sh, pausedByUs) : pausedByUs && clickVisible((t) => t.startsWith("Resume Simulation"))));
	};

	// ------------------------------------------------------------------ game-day slots: schedule page
	const SLOT_COLORS = ["#6f42c1", "#0d6efd", "#198754", "#d63384", "#fd7e14"];
	const slotText = (S) => (S.key === "SUN11" || S.key === "SUN1" ? `${S.date} · ${S.time} ET` : `${S.key === "TNF" || S.key === "SNF" || S.key === "MNF" ? "📺 " : ""}${S.name} · ${S.date} · ${S.time} ET`);
	const cardTids = (card) => [...new Set([...card.querySelectorAll('a[href*="/roster/"]')].map((a) => {
		const m = /\/roster\/[^/]*_(\d+)(\/|$)/.exec(a.getAttribute("href") || "");
		return m ? Number(m[1]) : null;
	}).filter((x) => x !== null))];
	const gameForCard = (W, card) => {
		const t = cardTids(card);
		if (t.length !== 2) return null;
		return W.games.find((x) => t.includes(x.home) && t.includes(x.away)) || null;
	};
	const scheduleCards = () => {
		const out = new Set();
		for (const el of document.querySelectorAll(".score-box-left-wrapper")) {
			const c = el.closest(".d-flex.flex-wrap > div");
			if (c) out.add(c);
		}
		return [...out];
	};
	const SCHED = { key: "", W: null, busy: false };
	let SIMMING = false;

	const toast = () => {
		const el = document.createElement("div");
		el.style.cssText = "position:fixed;top:70px;left:50%;transform:translateX(-50%);z-index:2060;background:#0b1f3a;color:#fff;padding:10px 18px;border-radius:8px;font-weight:600;box-shadow:0 6px 24px rgba(0,0,0,.35);font-size:14px;";
		document.body.appendChild(el);
		return { set: (t) => (el.textContent = t), close: () => el.remove() };
	};
	// play the games that kick off before this one (and, when watching, the ones that kick off with it), then this one
	const runSlate = async (gids, gm, action) => {
		if (SIMMING) return;
		SIMMING = true;
		const tt = toast();
		try {
			const W = await weekInfo({});
			const todo = (W ? W.games : []).filter((x) => !x.played && gids.includes(x.gid)).sort((a, b) => a.slot - b.slot || a.gid - b.gid);
			for (let i = 0; i < todo.length; i++) {
				const x = todo[i];
				tt.set(`📺 ${W.slots[x.slot].short}: ${nick(x.awayAbbrev)} at ${nick(x.homeAbbrev)} (${i + 1} of ${todo.length})`);
				await window.bbgm.toWorker("actions", "simGame", x.gid);
			}
			if (gm && action) {
				tt.set(action === "liveGame" ? "🏈 Kickoff! Heading to the game…" : "Playing it…");
				await window.bbgm.toWorker("actions", action, gm.gid);
			}
		} catch (e) {
			console.log("Broadcast Booth (slate): " + e.message);
		} finally {
			tt.close();
			SIMMING = false;
			SCHED.key = "";
		}
	};
	window.addEventListener(
		"click",
		(e) => {
			const btn = e.target && e.target.closest ? e.target.closest("button") : null;
			if (!btn) return;
			const t = btn.textContent.replace(/\s+/g, "");
			if (t !== "Watchgame" && t !== "Simgame") return;
			const W = SCHED.W;
			if (!W || !W.today || !/\/daily_schedule/.test(location.pathname)) return;
			const card = btn.closest(".d-flex.flex-wrap > div");
			const gm = card ? gameForCard(W, card) : null;
			if (!gm || gm.slot === undefined) return;
			const watch = t === "Watchgame";
			const prior = W.games.filter((x) => !x.played && x.gid !== gm.gid && (x.slot < gm.slot || (watch && x.slot === gm.slot)));
			if (!prior.length) return; // nothing kicks off first, let Football GM handle it
			e.preventDefault();
			e.stopImmediatePropagation();
			if (!SIMMING) runSlate(prior.map((x) => x.gid), gm, watch ? "liveGame" : "simGame");
		},
		true,
	);

	const renderBanner = (W, cards) => {
		const first = cards[0] && cards[0].parentElement;
		const old = document.getElementById("pgm-week-banner");
		if (!W || !first) {
			if (old) old.remove();
			return;
		}
		const parent = first.parentElement;
		let b = old;
		if (!b) {
			b = document.createElement("div");
			b.id = "pgm-week-banner";
			b.className = "mb-3";
		}
		const anchor = [...parent.children].find((x) => x.tagName === "H2" || x === first) || first;
		if (b.parentElement !== parent || b.nextElementSibling !== anchor) parent.insertBefore(b, anchor);
		const mine = W.games.find((x) => x.home === W.userTid || x.away === W.userTid);
		const before = mine ? W.games.filter((x) => !x.played && x.slot < mine.slot) : [];
		const S = mine ? W.slots[mine.slot] : null;
		const opp = mine ? (mine.home === W.userTid ? `vs ${nick(mine.awayAbbrev)}` : `at ${nick(mine.homeAbbrev)}`) : "";
		const html = `<div class="d-flex flex-wrap align-items-center gap-2"><span class="fw-bold">Week ${W.week}</span><span class="text-body-secondary">${esc(W.slots[0].date)} – ${esc(W.slots[4].date)}</span>${mine ? `<span>· Our game: <b style="color:${SLOT_COLORS[mine.slot]}">${esc(S.key === "SUN11" || S.key === "SUN1" ? `Sunday ${S.time}` : S.name + " · " + S.time)}</b> ${esc(opp)}${mine.played ? " (final)" : ""}</span>` : ""}${W.today && before.length ? `<button type="button" class="btn btn-sm btn-secondary pgm-play-before">▶ Play the ${plural(before.length, "game", "games")} before our kickoff</button>` : ""}</div>`;
		if (b.dataset.html !== html) {
			b.dataset.html = html;
			b.innerHTML = html;
			const btn = b.querySelector(".pgm-play-before");
			if (btn) btn.addEventListener("click", () => runSlate(before.map((x) => x.gid), null, null));
		}
	};
	const decorateSchedule = (W, cards) => {
		for (const c of cards) {
			const gm = W ? gameForCard(W, c) : null;
			let l = c.querySelector(":scope > .pgm-slot");
			if (!gm || gm.slot === undefined) {
				if (l) l.remove();
				c.style.order = "";
				continue;
			}
			const S = W.slots[gm.slot];
			if (!l) {
				l = document.createElement("div");
				l.className = "pgm-slot";
				c.insertBefore(l, c.firstChild);
			}
			const txt = slotText(S);
			if (l.textContent !== txt) l.textContent = txt;
			l.style.cssText = `font-size:.8rem;font-weight:600;color:${SLOT_COLORS[gm.slot]};margin:0 0 2px 2px;`;
			const ord = String(gm.slot * 1000 + (gm.gid % 1000));
			if (c.style.order !== ord) c.style.order = ord;
		}
		renderBanner(W, cards);
	};
	const schedTick = async () => {
		const m = /^\/l\/\d+\/daily_schedule(?:\/(\d+)(?:\/(\d+))?)?/.exec(location.pathname);
		if (!m) {
			const old = document.getElementById("pgm-week-banner");
			if (old) old.remove();
			SCHED.key = "";
			return;
		}
		const cards = scheduleCards();
		if (!cards.length) return;
		const key = `${location.pathname}|${cards.length}|${cards.filter((c) => c.querySelector("button")).length}`;
		if (key !== SCHED.key && !SCHED.busy && !SIMMING) {
			SCHED.busy = true;
			try {
				SCHED.W = await weekInfo(m[2] ? { season: Number(m[1]), day: Number(m[2]) } : m[1] ? { season: Number(m[1]) } : {});
			} catch (e) {
				SCHED.W = null;
			}
			SCHED.key = key;
			SCHED.busy = false;
		}
		decorateSchedule(SCHED.W, cards);
	};
	setInterval(() => {
		schedTick().catch((e) => console.log("Broadcast Booth (schedule): " + e.message));
	}, 1000);

	// ------------------------------------------------------------------ game-day slots: score ticker during the game
	const TICK = { W: null, our: null, clock: { q: 1, min: 15, final: false }, el: null, built: "" };
	const tickerReset = () => {
		TICK.W = null;
		TICK.our = null;
		TICK.clock = { q: 1, min: 15, final: false };
		TICK.built = "";
		TICK.t0 = undefined;
		if (TICK.el) TICK.el.remove();
		TICK.el = null;
		document.body.style.paddingBottom = "";
		toggle.style.bottom = "12px";
	};
	const loadTicker = async () => {
		const B = readBoxFull();
		if (!B) return;
		const W = await weekInfo({ abbrevs: B.teams.map((t) => t.abbrev) });
		if (!W) return;
		const tids = new Set();
		for (const x of W.games) if (B.teams.some((t) => t.abbrev === x.homeAbbrev) && B.teams.some((t) => t.abbrev === x.awayAbbrev)) tids.add(x.gid);
		const our = W.games.find((x) => tids.has(x.gid));
		if (!our) return;
		TICK.W = W;
		TICK.our = our;
		renderTicker();
	};
	const tickerAdvance = (r) => {
		const s = stripStats(r.orig || "");
		let m;
		if (r.header && r.header.clock) TICK.clock.min = toSec(r.header.clock) / 60;
		if ((m = /^Start of (\d)(?:st|nd|rd|th) quarter$/.exec(s))) {
			TICK.clock.q = Number(m[1]);
			TICK.clock.min = 15;
		}
		if (/^Start of .*overtime$/.test(s)) {
			TICK.clock.q = 5;
			TICK.clock.min = 10;
		}
		if (s === "Two minute warning") TICK.clock.min = 2;
		if (s === "End of game") TICK.clock.final = true;
	};
	const ptsOfEvent = (e) => {
		if (e.safety) return [1 - e.t, 2];
		if (e.type === "extraPoint") return e.made ? [e.t, 1] : null;
		if (e.type === "fieldGoal") return e.made ? [e.t, 3] : null;
		if (e.type === "twoPointConversionFailed") return null;
		if (e.td) return [e.t, e.twoPointConversionTeam !== undefined ? 2 : 6];
		return null;
	};
	// another game's score at the same point on the clock as ours
	const scoreAt = (x, clk) => {
		if (clk.final) return { h: x.hp, a: x.ap, final: true };
		const sums = [[], []];
		for (const e of x.ss) {
			const p = ptsOfEvent(e);
			if (!p) continue;
			const qi = (e.quarter || 1) - 1;
			sums[p[0]][qi] = (sums[p[0]][qi] || 0) + p[1];
		}
		const exact = [x.hq, x.aq].every((arr, ti) => arr.every((v, qi) => (sums[ti][qi] || 0) === v));
		let h = 0;
		let a = 0;
		if (exact) {
			for (const e of x.ss) {
				const p = ptsOfEvent(e);
				if (!p) continue;
				if (e.quarter < clk.q || (e.quarter === clk.q && e.clock >= clk.min - 1e-6)) {
					if (p[0] === 0) h += p[1];
					else a += p[1];
				}
			}
		} else {
			for (let qi = 0; qi < clk.q - 1; qi++) {
				h += x.hq[qi] || 0;
				a += x.aq[qi] || 0;
			}
		}
		if (clk.q > x.hq.length) return { h: x.hp, a: x.ap, final: true };
		return { h, a, final: false };
	};
	const clockLabel = (clk) => {
		if (clk.final) return "FINAL";
		if (clk.q === 3 && clk.min >= 15 - 1e-6) return "HALFTIME";
		const mm = Math.floor(clk.min + 1e-6);
		const ss = Math.round((clk.min - mm) * 60);
		const c = `${mm}:${String(ss === 60 ? 0 : ss).padStart(2, "0")}`;
		return clk.q >= 5 ? `OT ${c}` : `Q${clk.q} ${c}`;
	};
	const injectTickerStyle = () => {
		if (document.getElementById("pgm-ticker-style")) return;
		const st = document.createElement("style");
		st.id = "pgm-ticker-style";
		st.textContent = `
.pgm-ticker{position:fixed;left:0;right:0;bottom:0;height:34px;z-index:1990;display:flex;align-items:center;background:#0b1f3a;color:#fff;font-size:13px;font-weight:600;box-shadow:0 -2px 8px rgba(0,0,0,.3);font-variant-numeric:tabular-nums}
.pgm-ticker-tag{flex:0 0 auto;padding:0 12px;height:100%;display:flex;align-items:center;background:#c8102e;letter-spacing:.04em;white-space:nowrap}
.pgm-ticker-track{flex:1;overflow:hidden;height:100%;position:relative}
.pgm-ticker-inner{display:inline-flex;white-space:nowrap;height:100%;align-items:center}
.pgm-ticker-inner.run{animation:pgmTick var(--dur,60s) linear infinite}
.pgm-ticker-inner:hover{animation-play-state:paused}
.pgm-tk-item{padding:0 16px;border-right:1px solid rgba(255,255,255,.18)}
.pgm-tk-lbl{color:#ffd166;margin-right:8px;font-size:11px;letter-spacing:.06em}
.pgm-tk-lead{color:#fff}.pgm-tk-trail{color:rgba(255,255,255,.7);font-weight:500}
@keyframes pgmTick{from{transform:translateX(0)}to{transform:translateX(-50%)}}`;
		document.head.appendChild(st);
	};
	const renderTicker = () => {
		const W = TICK.W;
		const our = TICK.our;
		if (!W || !our || !enabled || !document.querySelector(".live-game-playbyplay")) {
			if (TICK.el) TICK.el.style.display = "none";
			document.body.style.paddingBottom = "";
			toggle.style.bottom = "12px";
			return;
		}
		const same = W.games.filter((x) => x.slot === our.slot && x.gid !== our.gid && x.played);
		const bySlot = (a, b) => a.slot - b.slot || a.gid - b.gid;
		const earlier = W.games.filter((x) => x.slot < our.slot && x.played).sort(bySlot);
		const later = W.games.filter((x) => x.slot > our.slot || (x.slot === our.slot && !x.played && x.gid !== our.gid)).sort(bySlot);
		if (!same.length && !earlier.length && !later.length) return;
		injectTickerStyle();
		const S = W.slots[our.slot];
		const clk = TICK.clock;
		const items = [];
		const scoreItem = (x, sc, lbl) => {
			const aLead = sc.a > sc.h;
			const hLead = sc.h > sc.a;
			return `<span class="pgm-tk-item">${lbl ? `<span class="pgm-tk-lbl">${esc(lbl)}</span>` : ""}<span class="${aLead ? "pgm-tk-lead" : "pgm-tk-trail"}">${esc(x.awayAbbrev)} ${sc.a}</span> &nbsp;<span class="${hLead ? "pgm-tk-lead" : "pgm-tk-trail"}">${esc(x.homeAbbrev)} ${sc.h}</span>${sc.final ? ' <span class="pgm-tk-lbl" style="margin:0 0 0 6px">F</span>' : ""}</span>`;
		};
		for (const x of same) items.push(scoreItem(x, scoreAt(x, clk), ""));
		for (const x of earlier) items.push(scoreItem(x, { h: x.hp, a: x.ap, final: false }, `${W.slots[x.slot].short} FINAL`));
		for (const x of later) items.push(`<span class="pgm-tk-item"><span class="pgm-tk-lbl">${esc(W.slots[x.slot].short)} ${esc(W.slots[x.slot].time)}</span>${esc(x.awayAbbrev)} at ${esc(x.homeAbbrev)}</span>`);
		const tag = `📺 ${S.short} · ${clockLabel(clk)}`;
		const body = items.join("");
		if (!TICK.el) {
			TICK.el = document.createElement("div");
			TICK.el.className = "pgm-ticker";
			TICK.el.innerHTML = `<div class="pgm-ticker-tag"></div><div class="pgm-ticker-track"><div class="pgm-ticker-inner"></div></div>`;
			document.body.appendChild(TICK.el);
		}
		TICK.el.style.display = "";
		document.body.style.paddingBottom = "40px";
		toggle.style.bottom = "46px";
		const tagEl = TICK.el.querySelector(".pgm-ticker-tag");
		if (tagEl.textContent !== tag) tagEl.textContent = tag;
		if (TICK.built !== body) {
			TICK.built = body;
			const inner = TICK.el.querySelector(".pgm-ticker-inner");
			const track = TICK.el.querySelector(".pgm-ticker-track");
			inner.classList.remove("run");
			inner.innerHTML = body;
			if (inner.scrollWidth > track.clientWidth) {
				// loop it like a TV crawl; keep the scroll position when only the scores change
				inner.innerHTML = body + body;
				inner.style.setProperty("--dur", `${Math.max(20, Math.round(inner.scrollWidth / 2 / 55))}s`);
				inner.classList.add("run");
				if (TICK.t0 === undefined) TICK.t0 = performance.now();
				const anim = inner.getAnimations ? inner.getAnimations()[0] : null;
				if (anim) anim.currentTime = (performance.now() - TICK.t0) % (anim.effect.getTiming().duration || 60000);
			}
		}
	};

	// on/off switch
	const toggle = document.createElement("button");
	const paintToggle = () => {
		toggle.textContent = enabled ? "🎙 Broadcast: ON" : "🎙 Broadcast: OFF";
	};
	toggle.className = "btn btn-sm btn-light-bordered";
	toggle.style.cssText = "position:fixed;left:12px;bottom:12px;z-index:2000;display:none;";
	toggle.addEventListener("click", () => {
		enabled = !enabled;
		try {
			localStorage.setItem(PREF_KEY, enabled ? "on" : "off");
		} catch {}
		paintToggle();
		const c = document.querySelector(".live-game-playbyplay");
		if (c) for (const el of c.children) info.has(el) && show(info.get(el));
		renderTicker();
	});
	paintToggle();
	const mountToggle = () => {
		if (!toggle.isConnected && document.body) document.body.appendChild(toggle);
	};

	let watched = null;
	let observer = null;
	setInterval(() => {
		const c = document.querySelector(".live-game-playbyplay");
		mountToggle();
		toggle.style.display = c ? "" : "none";
		if (!c && TICK.el) tickerReset();
		if (c && c !== watched) {
			watched = c;
			if (observer) observer.disconnect();
			tickerReset();
			loadTeamNames().finally(() => {
				observer = new MutationObserver(() => processAll(c));
				observer.observe(c, { childList: true });
				processAll(c);
				let tries = 0;
				const tryTicker = () => {
					if (watched !== c || TICK.W) return;
					tries += 1;
					loadTicker()
						.catch((e) => console.log("Broadcast Booth (ticker): " + e.message))
						.finally(() => {
							if (!TICK.W && tries < 10 && watched === c) setTimeout(tryTicker, 2000);
						});
				};
				tryTicker();
			});
		}
	}, 500);
})();
