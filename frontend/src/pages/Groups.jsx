import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../api/client";
import { useAuth } from "../context/AuthContext";

function Groups() {
  const [groups, setGroups] = useState([]);
  const [name, setName] = useState("");
  const [memberEmails, setMemberEmails] = useState("");
  const [error, setError] = useState("");
  const { user, logout } = useAuth();

  const loadGroups = () => {
    api.get("/groups").then((res) => setGroups(res.data));
  };

  useEffect(() => {
    loadGroups();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const emails = memberEmails
        .split(",")
        .map((e) => e.trim())
        .filter(Boolean);
      await api.post("/groups", { name, member_emails: emails });
      setName("");
      setMemberEmails("");
      loadGroups();
    } catch (err) {
      setError(err.response?.data?.error || "Could not create group");
    }
  };

  return (
    <div>
      <header className="page-header">
        <h2>Your groups</h2>
        <div>
          <span className="muted">{user?.name}</span>
          <button className="link-button" onClick={logout}>
            Log out
          </button>
        </div>
      </header>

      <form onSubmit={handleCreate} className="inline-form">
        <input
          type="text"
          placeholder="New group name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Member emails, comma separated"
          value={memberEmails}
          onChange={(e) => setMemberEmails(e.target.value)}
        />
        <button type="submit">Create group</button>
      </form>
      {error && <p className="error-text">{error}</p>}

      {groups.length === 0 ? (
        <p className="muted">No groups yet — create one above.</p>
      ) : (
        <ul className="card-list">
          {groups.map((g) => (
            <li key={g.id} className="card">
              <Link to={`/groups/${g.id}`}>{g.name}</Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Groups;
