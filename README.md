# SplitEase

SplitEase is a simplified Splitwise-style expense splitter. Create a group with
friends, log shared expenses, and SplitEase works out exactly who owes whom —
and the smallest set of payments needed to settle up.

## Why this exists

Splitting group expenses (trips, flatshares, dinners) by hand is error-prone.
SplitEase keeps a running ledger per group and reduces it down to the minimum
number of payments required to clear every debt, instead of everyone paying
everyone back individually.

## Tech stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, SQLite (dev)
- **Frontend:** React (Vite), React Router, Axios
- **Auth:** JWT-based

## Project structure

```
SplitEase/
├── backend/      # Flask REST API
└── frontend/     # React single-page app
```

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md)
for setup instructions for each half of the app.

## Core features

- Sign up / log in
- Create groups and add members
- Log expenses with an equal split or a custom split
- View each member's net balance in a group
- "Settle up" view showing the minimum number of transactions to clear all debts

## How balances are calculated

Every expense has a payer and a set of splits (who owes how much of it). A
member's net balance in a group is:

```
net balance = total they paid − total of their own split shares
```

A positive balance means the group owes them money; negative means they owe
the group. The settle-up algorithm then greedily matches the largest debtor
with the largest creditor, repeating until every balance is zero — this
minimizes the number of payments needed instead of naively paying back every
individual expense.
