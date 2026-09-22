function SettleUp({ transactions }) {
  if (transactions.length === 0) {
    return <p className="muted">Everyone is settled up.</p>;
  }

  return (
    <ul className="card-list">
      {transactions.map((t, i) => (
        <li key={i} className="card">
          <strong>{t.from.name}</strong> pays <strong>{t.to.name}</strong> ₹
          {t.amount.toFixed(2)}
        </li>
      ))}
    </ul>
  );
}

export default SettleUp;
