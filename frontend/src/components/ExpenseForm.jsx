import { useState } from "react";

import api from "../api/client";

function ExpenseForm({ group, onExpenseAdded }) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [paidBy, setPaidBy] = useState(group.members[0]?.id || "");
  const [splitType, setSplitType] = useState("equal");
  const [customAmounts, setCustomAmounts] = useState({});
  const [error, setError] = useState("");

  const handleCustomChange = (userId, value) => {
    setCustomAmounts((prev) => ({ ...prev, [userId]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const payload = {
      description,
      amount: parseFloat(amount),
      paid_by: Number(paidBy),
    };

    if (splitType === "custom") {
      payload.splits = group.members.map((m) => ({
        user_id: m.id,
        amount_owed: parseFloat(customAmounts[m.id] || 0),
      }));
    }

    try {
      await api.post(`/groups/${group.id}/expenses`, payload);
      setDescription("");
      setAmount("");
      setCustomAmounts({});
      onExpenseAdded();
    } catch (err) {
      setError(err.response?.data?.error || "Could not add expense");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="expense-form">
      <input
        type="text"
        placeholder="What was it for?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <input
        type="number"
        step="0.01"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        required
      />

      <label>
        Paid by
        <select value={paidBy} onChange={(e) => setPaidBy(e.target.value)}>
          {group.members.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
      </label>

      <div className="split-toggle">
        <label>
          <input
            type="radio"
            checked={splitType === "equal"}
            onChange={() => setSplitType("equal")}
          />
          Split equally
        </label>
        <label>
          <input
            type="radio"
            checked={splitType === "custom"}
            onChange={() => setSplitType("custom")}
          />
          Custom split
        </label>
      </div>

      {splitType === "custom" && (
        <div className="custom-splits">
          {group.members.map((m) => (
            <label key={m.id}>
              {m.name}
              <input
                type="number"
                step="0.01"
                value={customAmounts[m.id] || ""}
                onChange={(e) => handleCustomChange(m.id, e.target.value)}
              />
            </label>
          ))}
        </div>
      )}

      {error && <p className="error-text">{error}</p>}
      <button type="submit">Add expense</button>
    </form>
  );
}

export default ExpenseForm;
