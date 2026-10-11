// ==UserScript==
// @name         Football GM: Broadcast Booth
// @namespace    was-dynasty-fbgm
// @version      1.0
// @description  Turns Football GM's live play-by-play into TV-style commentary. Real names, yards, downs, score and in-game stat callbacks; the flavor is made up to fit. Hover any line to see the original.
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
				ctx.score[r.t] = r.score.mine;
				ctx.scoredLast = r.t;
				ctx.otherScore = r.score.theirs;
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
			const o = ctx.opp(r.t);
			const mine = r.score.mine;
			const theirs = r.score.theirs;
			const before = ctx.pts(r.t);
			if (mine > theirs && before <= theirs) return ` ${nick(r.t)} take the lead, ${mine}-${theirs}!`;
			if (mine === theirs) return ` We're all tied up at ${mine}!`;
			if (mine > theirs) return ` ${nick(r.t)} up ${mine}-${theirs}.`;
			return ` ${nick(o)} still lead, ${theirs}-${mine}.`;
		};
		const clutch = S.late && S.close;

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
			return { html: esc(line + fdTag(yds) + extra), big: yds >= 25 };
		}
		if ((m = /^Incomplete pass to (.+)$/.exec(s))) {
			const wr = last(m[1]);
			if (S.h && S.h.down === 4) return { html: `<b>${esc(p([`Fourth-down throw for ${wr}… INCOMPLETE!`, `It's thrown for ${wr}… no! Falls incomplete on fourth down!`, `${wr} can't come up with it on fourth down!`]))}</b>`, big: true };
			return p([`Thrown for ${wr}… incomplete.`, `Overthrown — ${wr} couldn't get to it.`, `Broken up! Incomplete, intended for ${wr}.`, `Off the fingertips of ${wr}, incomplete.`, `${wr} can't come up with it.`]);
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
			return { html: esc(line + fdTag(yds) + milestone("rushing", m[1], before, yds, [100, 150, 200])), big: yds >= 20 };
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
			return p([`${k} brings it out ${yds} yards.`, `${k} returns it ${yds}.`]);
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
			return p([`${k} returns it ${yds}.`, `${k} brings it back ${yds} yards.`]);
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
			if (S.late && S.diff < 0) tail = `, down ${-S.diff} with ${h.clock} left. Everything on this snap!`;
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

	const processAll = (container) => {
		const entries = [...container.children].reverse(); // oldest first
		for (const el of entries) {
			const r = readEntry(el);
			if (r) apply(r);
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
		if (c && c !== watched) {
			watched = c;
			if (observer) observer.disconnect();
			loadTeamNames().finally(() => {
				observer = new MutationObserver(() => processAll(c));
				observer.observe(c, { childList: true });
				processAll(c);
			});
		}
	}, 500);
})();
