import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { mutate, setLeague, useLeague } from "../store";
import { deleteLeague, exportLeague } from "../db";
import type { Settings } from "../../engine/types";
import { Card, PageHead } from "../components/common";

export function SettingsPage() {
  const L = useLeague();
  const nav = useNavigate();
  const [name, setName] = useState(L.name);
  const [theme, setTheme] = useState<string>(() => document.documentElement.dataset.theme ?? "light");
  const [busy, setBusy] = useState(false);
  const set = <K extends keyof Settings>(k: K, v: Settings[K]) => mutate((LL) => void (LL.settings[k] = v));
  const applyTheme = (t: string) => {
    setTheme(t);
    document.documentElement.dataset.theme = t;
    try {
      localStorage.setItem("hd-theme", t);
    } catch {
      // ignore
    }
  };
  return (
    <div>
      <PageHead title="Settings" />
      <div className="grid g2">
        <Card title="League">
          <div className="col gap-12">
            <div className="field">
              <label>League name</label>
              <div className="row">
                <input className="input" style={{ flex: 1 }} value={name} onChange={(e) => setName(e.target.value)} />
                <button className="btn" onClick={() => mutate((LL) => void (LL.name = name.trim() || LL.name))}>
                  Save
                </button>
              </div>
            </div>
            <div className="field">
              <label>Theme</label>
              <div className="btn-group">
                <button className={`btn ${theme === "light" ? "on" : ""}`} onClick={() => applyTheme("light")}>
                  Light
                </button>
                <button className={`btn ${theme === "dark" ? "on" : ""}`} onClick={() => applyTheme("dark")}>
                  Dark
                </button>
              </div>
            </div>
          </div>
        </Card>
        <Card title="Rules">
          <div className="col gap-12">
            <label className="check">
              <input type="checkbox" checked={L.settings.autoRecruit} onChange={(e) => set("autoRecruit", e.target.checked)} /> Let my staff handle recruiting (auto)
            </label>
            <label className="check">
              <input type="checkbox" checked={L.settings.portal} onChange={(e) => set("portal", e.target.checked)} /> Transfer portal
            </label>
            <label className="check">
              <input type="checkbox" checked={L.settings.nil} onChange={(e) => set("nil", e.target.checked)} /> NIL deals
            </label>
            <label className="check">
              <input type="checkbox" checked={L.settings.canBeFired} onChange={(e) => set("canBeFired", e.target.checked)} /> You can be fired
            </label>
            <label className="check">
              <input type="checkbox" checked={L.settings.injuries} onChange={(e) => set("injuries", e.target.checked)} /> Injuries
            </label>
            <label className="check">
              <input type="checkbox" checked={L.settings.keepAllBoxScores} onChange={(e) => set("keepAllBoxScores", e.target.checked)} /> Keep box scores for every game (uses more storage; your games are always kept)
            </label>
            <div className="row">
              <div className="field" style={{ flex: 1 }}>
                <label>NCAA field (from next Selection Sunday)</label>
                <select className="select" value={L.settings.bracketSize} onChange={(e) => set("bracketSize", Number(e.target.value) as Settings["bracketSize"])}>
                  <option value={64}>64 teams</option>
                  <option value={68}>68 teams</option>
                  <option value={76}>76 teams</option>
                </select>
              </div>
              <div className="field" style={{ flex: 1 }}>
                <label>Recruiting AI</label>
                <select className="select" value={L.settings.recruitingDifficulty} onChange={(e) => set("recruitingDifficulty", Number(e.target.value) as Settings["recruitingDifficulty"])}>
                  <option value={1}>Easy</option>
                  <option value={2}>Normal</option>
                  <option value={3}>Hard</option>
                </select>
              </div>
              <div className="field" style={{ flex: 1 }}>
                <label>Home-court edge</label>
                <select className="select" value={L.settings.homeCourt} onChange={(e) => set("homeCourt", Number(e.target.value))}>
                  <option value={0}>None</option>
                  <option value={2}>Small</option>
                  <option value={3.5}>Normal</option>
                  <option value={5}>Large</option>
                </select>
              </div>
            </div>
          </div>
        </Card>
        <Card title="Backup">
          <p className="small muted" style={{ marginTop: 0 }}>
            Your league lives in this browser's storage. Export a backup file (every season, player, box score and record) and import it from the start screen on any computer.
          </p>
          <button
            className="btn btn-primary"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                const blob = await exportLeague(L);
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                const safe = L.name.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
                a.download = `hardwood-${safe}-${L.season}.hdsave${blob.type === "application/x-ndjson" ? "" : ".gz"}`;
                a.click();
                setTimeout(() => URL.revokeObjectURL(a.href), 2000);
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy ? "Exporting…" : "Export league"}
          </button>
        </Card>
        <Card title="Danger zone">
          <button
            className="btn btn-danger"
            onClick={async () => {
              if (!confirm(`Delete "${L.name}" and all of its history? This cannot be undone.`)) return;
              await deleteLeague(L.id);
              setLeague(null);
              nav("/");
            }}
          >
            Delete this league
          </button>
        </Card>
      </div>
    </div>
  );
}
