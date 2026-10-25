import { useEffect, useState } from "react";
import { HashRouter, Navigate, Outlet, Route, Routes, useNavigate, useParams } from "react-router-dom";
import { switchCode } from "./cloud";
import { openLeague, useLeagueMaybe } from "./store";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { NewLeague } from "./pages/NewLeague";
import { Dashboard } from "./pages/Dashboard";
import { Inbox } from "./pages/Inbox";
import { Roster } from "./pages/Roster";
import { PlayerPage } from "./pages/Player";
import { Tactics } from "./pages/Tactics";
import { RotationPage } from "./pages/Rotation";
import { Practice } from "./pages/Practice";
import { Schedule } from "./pages/Schedule";
import { GamePage } from "./pages/Game";
import { Scores } from "./pages/Scores";
import { Standings } from "./pages/Standings";
import { Rankings } from "./pages/Rankings";
import { Tournaments } from "./pages/Tournaments";
import { RecruitingBoard } from "./pages/Recruiting";
import { Targets } from "./pages/Targets";
import { ClassRankings } from "./pages/Classes";
import { Portal } from "./pages/Portal";
import { TeamPage } from "./pages/Team";
import { Stats } from "./pages/Stats";
import { Awards } from "./pages/Awards";
import { LeagueHistory } from "./pages/History";
import { Records } from "./pages/Records";
import { CoachPage } from "./pages/Coach";
import { DraftPage } from "./pages/Draft";
import { Transfers } from "./pages/Transfers";
import { SettingsPage } from "./pages/Settings";
import { SeasonReview } from "./pages/SeasonReview";
import { Signing } from "./pages/Signing";
import { Guide } from "./pages/Guide";
import { Prep } from "./pages/Prep";

function LeagueRoot() {
  const { lid } = useParams();
  const L = useLeagueMaybe();
  const [missing, setMissing] = useState(false);
  useEffect(() => {
    if (!lid) return;
    openLeague(lid).then((x) => setMissing(!x));
  }, [lid]);
  if (missing) return <Navigate to="/" replace />;
  if (!L || L.id !== lid) return <div className="empty" style={{ paddingTop: 120 }}>Loading league…</div>;
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
}

/** #/link/CODE: use a save code from another device, then show its leagues. */
function LinkCode() {
  const { code } = useParams();
  const nav = useNavigate();
  const [bad, setBad] = useState(false);
  useEffect(() => {
    void switchCode(code ?? "").then((ok) => (ok ? nav("/?linked=1", { replace: true }) : setBad(true)));
  }, [code]);
  return <div className="empty" style={{ paddingTop: 120 }}>{bad ? "That save code doesn't look right." : "Linking your saves…"}</div>;
}

function ProgramRedirect() {
  const L = useLeagueMaybe();
  if (!L) return null;
  return <Navigate to={`/l/${L.id}/team/${L.userTid}?tab=history`} replace />;
}

export function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/new" element={<NewLeague />} />
        <Route path="/link/:code" element={<LinkCode />} />
        <Route path="/l/:lid" element={<LeagueRoot />}>
          <Route index element={<Dashboard />} />
          <Route path="inbox" element={<Inbox />} />
          <Route path="roster" element={<Roster />} />
          <Route path="player/:pid" element={<PlayerPage />} />
          <Route path="tactics" element={<Tactics />} />
          <Route path="rotation" element={<RotationPage />} />
          <Route path="practice" element={<Practice />} />
          <Route path="schedule" element={<Schedule />} />
          <Route path="prep" element={<Prep />} />
          <Route path="game/:gid" element={<GamePage />} />
          <Route path="scores" element={<Scores />} />
          <Route path="standings" element={<Standings />} />
          <Route path="rankings" element={<Rankings />} />
          <Route path="tournaments" element={<Tournaments />} />
          <Route path="recruiting" element={<RecruitingBoard />} />
          <Route path="targets" element={<Targets />} />
          <Route path="classes" element={<ClassRankings />} />
          <Route path="portal" element={<Portal />} />
          <Route path="team/:tid" element={<TeamPage />} />
          <Route path="program" element={<ProgramRedirect />} />
          <Route path="stats" element={<Stats />} />
          <Route path="awards" element={<Awards />} />
          <Route path="history" element={<LeagueHistory />} />
          <Route path="records" element={<Records />} />
          <Route path="coach" element={<CoachPage />} />
          <Route path="draft" element={<DraftPage />} />
          <Route path="transfers" element={<Transfers />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="season-review" element={<SeasonReview />} />
          <Route path="signing" element={<Signing />} />
          <Route path="guide" element={<Guide />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </HashRouter>
  );
}
