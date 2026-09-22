import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import api from "../api/client";
import ExpenseForm from "../components/ExpenseForm";

function GroupDetail() {
  const { groupId } = useParams();
  const [group, setGroup] = useState(null);
  const [expenses, setExpenses] = useState([]);

  const loadGroup = () => api.get(`/groups/${groupId}`).then((res) => setGroup(res.data));
  const loadExpenses = () =>
    api.get(`/groups/${groupId}/expenses`).then((res) => setExpenses(res.data));

  useEffect(() => {
    loadGroup();
    loadExpenses();
  }, [groupId]);

  if (!group) return <p>Loading...</p>;

  const memberName = (userId) =>
    group.members.find((m) => m.id === userId)?.name || "Unknown";

  return (
    <div>
      <p>
        <Link to="/groups">&larr; All groups</Link>
      </p>
      <header className="page-header">
        <h2>{group.name}</h2>
      </header>
      <p className="muted">Members: {group.members.map((m) => m.name).join(", ")}</p>

      <h3>Add an expense</h3>
      <ExpenseForm group={group} onExpenseAdded={loadExpenses} />

      <h3>Expenses</h3>
      {expenses.length === 0 ? (
        <p className="muted">No expenses yet.</p>
      ) : (
        <ul className="card-list">
          {expenses.map((e) => (
            <li key={e.id} className="card">
              <strong>{e.description}</strong> — ₹{e.amount.toFixed(2)}
              <div className="muted">Paid by {memberName(e.paid_by)}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default GroupDetail;
