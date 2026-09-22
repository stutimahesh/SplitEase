import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./context/AuthContext";
import GroupDetail from "./pages/GroupDetail";
import Groups from "./pages/Groups";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p>Loading...</p>;
  return user ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <div className="app-shell">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/groups"
          element={
            <RequireAuth>
              <Groups />
            </RequireAuth>
          }
        />
        <Route
          path="/groups/:groupId"
          element={
            <RequireAuth>
              <GroupDetail />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/groups" replace />} />
      </Routes>
    </div>
  );
}

export default App;
