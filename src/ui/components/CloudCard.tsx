import { useEffect, useState } from "react";
import { cloudOn, formatCode, getCode, linkFor, saveAllNow, setCloudOn, switchCode, useCloudStatus } from "../cloud";
import { Card } from "./common";
import { Icon } from "./Icons";

export function ago(t: number): string {
  const s = Math.round((Date.now() - t) / 1000);
  if (s < 45) return "just now";
  const m = Math.round(s / 60);
  if (m < 60) return `${m} minute${m === 1 ? "" : "s"} ago`;
  const h = Math.round(m / 60);
  return h < 24 ? `${h} hour${h === 1 ? "" : "s"} ago` : new Date(t).toLocaleDateString();
}

export function cloudLine(st: ReturnType<typeof useCloudStatus>): string {
  if (st.state === "off") return "Off: leagues are saved in this browser only.";
  if (st.state === "saving") return "Saving to the cloud…";
  if (st.state === "error") return "Couldn't reach the cloud. It will try again in a couple of minutes.";
  if (st.last) return `Saved to the cloud ${ago(st.last)}.`;
  return "On: your leagues upload a few minutes after you play and whenever you leave.";
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    window.prompt("Copy this:", text);
    return false;
  }
}

/** Cloud save status, the save code, and linking another device. */
export function CloudCard() {
  const st = useCloudStatus();
  const [, tick] = useState(0);
  const [code, setCode] = useState(getCode());
  const [show, setShow] = useState(false);
  const [input, setInput] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const on = cloudOn();
  // keep "x minutes ago" fresh
  useEffect(() => {
    const t = setInterval(() => tick((x) => x + 1), 30000);
    return () => clearInterval(t);
  }, []);
  useEffect(() => setCode(getCode()), [st.state]);
  return (
    <Card title="Cloud saves" sub="Your leagues follow you to any device">
      <div className="col gap-12">
        <label className="check">
          <input
            type="checkbox"
            checked={on}
            onChange={(e) => {
              setCloudOn(e.target.checked);
              setCode(getCode());
            }}
          />{" "}
          Save my leagues to the cloud
        </label>
        <div className={`cloud-status ${st.state}`}>
          <Icon name="cloud" size={15} /> {cloudLine(st)}
          {on && st.state !== "saving" && (
            <button className="btn btn-sm" style={{ marginLeft: "auto" }} onClick={() => void saveAllNow()}>
              Save now
            </button>
          )}
        </div>
        {on && code && (
          <>
            <div className="field">
              <label>Your save code</label>
              <div className="row" style={{ gap: 6, flexWrap: "wrap" }}>
                <code className="save-code">{show ? formatCode(code) : "••••-••••-••••-" + code.slice(12)}</code>
                <button className="btn btn-sm" onClick={() => setShow(!show)}>
                  {show ? "Hide" : "Show"}
                </button>
                <button className="btn btn-sm" onClick={async () => setMsg((await copy(formatCode(code))) ? "Code copied." : null)}>
                  <Icon name="copy" size={13} /> Copy code
                </button>
                <button className="btn btn-sm" onClick={async () => setMsg((await copy(linkFor(code))) ? "Link copied. Open it on your other device." : null)}>
                  <Icon name="copy" size={13} /> Copy link
                </button>
              </div>
              <div className="small muted" style={{ marginTop: 6 }}>
                On your phone or another computer, open the link, or go to hardwood-dynasty.vercel.app and enter this code. Keep it private: anyone with it can load your leagues.
              </div>
            </div>
            <div className="field">
              <label>Have a code from another device?</label>
              <div className="row" style={{ gap: 6 }}>
                <input className="input" style={{ flex: 1, maxWidth: 260, fontFamily: "var(--mono, monospace)", textTransform: "uppercase" }} placeholder="XXXX-XXXX-XXXX-XXXX" value={input} onChange={(e) => setInput(e.target.value)} />
                <button
                  className="btn btn-primary"
                  disabled={!input.trim()}
                  onClick={async () => {
                    const ok = await switchCode(input);
                    if (ok) {
                      setCode(getCode());
                      setInput("");
                      setMsg("Linked. This device now saves under that code, and its leagues show up on the start screen.");
                    } else setMsg("That code doesn't look right. It has 16 letters and numbers.");
                  }}
                >
                  Use code
                </button>
              </div>
            </div>
          </>
        )}
        {msg && <div className="small" style={{ color: "var(--accent-ink)" }}>{msg}</div>}
      </div>
    </Card>
  );
}
