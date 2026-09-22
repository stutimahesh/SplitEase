import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./context/AuthContext";
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
              <p>Groups page coming next.</p>
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/groups" replace />} />
      </Routes>
    </div>
  );
}

export default App;
