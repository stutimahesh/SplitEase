function BalancesView({ balances }) {
  if (balances.length === 0) return null;

  return (
    <ul className="card-list">
      {balances.map(({ user, balance }) => (
        <li key={user.id} className="card balance-row">
          <span>{user.name}</span>
          {balance > 0 && <span className="positive">is owed ₹{balance.toFixed(2)}</span>}
          {balance < 0 && <span className="negative">owes ₹{Math.abs(balance).toFixed(2)}</span>}
          {balance === 0 && <span className="muted">settled up</span>}
        </li>
      ))}
    </ul>
  );
}

export default BalancesView;
