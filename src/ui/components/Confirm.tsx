// One styled confirmation popup for everything that spends coaching points.
// confirmSpend() asks yes/no; pickAndConfirm() has the user pick an option first.

import { useEffect, useState, useSyncExternalStore, type ReactNode } from "react";
import { Icon } from "./Icons";

export interface Choice {
  key: string;
  label: string;
  sub?: string;
}

interface Ask {
  id: number;
  title: string;
  body?: ReactNode;
  /** coaching points this costs, and how many the user has */
  cost?: { pts: number; have: number };
  ok: string;
  danger?: boolean;
  choices?: Choice[];
  resolve: (pick: string | null) => void;
}

type AskOpts = Omit<Ask, "id" | "resolve" | "choices">;

let current: Ask | null = null;
let nextId = 1;
const subs = new Set<() => void>();

function show(a: Ask | null) {
  current?.resolve(null);
  current = a;
  subs.forEach((f) => f());
}

/** Resolves true if the user confirms. */
export function confirmSpend(opts: AskOpts): Promise<boolean> {
  return new Promise((res) => show({ ...opts, id: nextId++, resolve: (v) => res(v !== null) }));
}

/** Resolves the chosen option's key, or null if the user backs out. */
export function pickAndConfirm(opts: AskOpts & { choices: Choice[] }): Promise<string | null> {
  return new Promise((res) => show({ ...opts, id: nextId++, resolve: res }));
}

function close(pick: string | null) {
  const a = current;
  current = null;
  subs.forEach((f) => f());
  a?.resolve(pick);
}

export function ConfirmHost() {
  const a = useSyncExternalStore(
    (f) => {
      subs.add(f);
      return () => subs.delete(f);
    },
    () => current,
  );
  // leaving the league cancels a question still open, so it can't come back in another league
  useEffect(() => () => close(null), []);
  return a ? <ConfirmModal key={a.id} a={a} /> : null;
}

function ConfirmModal({ a }: { a: Ask }) {
  const [pick, setPick] = useState<string | null>(null);
  const ready = !a.choices || pick !== null;
  const confirm = () => ready && close(a.choices ? pick : "yes");
  // focus moves into the popup (so Enter confirms it, instead of re-pressing the button that opened it)
  useEffect(() => {
    const key = (e: KeyboardEvent) => e.key === "Escape" && close(null);
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, []);
  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && close(null)}>
      <div className="modal confirm-modal" role="dialog" aria-modal="true" aria-label={a.title}>
        <div className="modal-h">
          <h2>{a.title}</h2>
        </div>
        <div className="modal-b">
          {a.body && <div className="confirm-body">{a.body}</div>}
          {a.choices && (
            <div className="confirm-choices">
              {a.choices.map((c, i) => (
                <button key={c.key} className={`confirm-choice${pick === c.key ? " on" : ""}`} autoFocus={i === 0} onClick={() => setPick(c.key)}>
                  <span>
                    <b>{c.label}</b>
                    {c.sub && <span className="tiny muted">{c.sub}</span>}
                  </span>
                  {pick === c.key && <Icon name="check" size={16} />}
                </button>
              ))}
            </div>
          )}
          {a.cost && a.cost.pts > 0 && (
            <div className="confirm-cost">
              <Icon name="bolt" size={14} />
              <span>
                Costs <b>{a.cost.pts}</b> coaching points. You'll have {a.cost.have - a.cost.pts} left this week.
              </span>
            </div>
          )}
        </div>
        <div className="modal-f">
          <button className="btn" onClick={() => close(null)}>
            Cancel
          </button>
          <button className={`btn ${a.danger ? "btn-danger-solid" : "btn-primary"}`} disabled={!ready} autoFocus={!a.choices} onClick={confirm}>
            {a.ok}
          </button>
        </div>
      </div>
    </div>
  );
}
