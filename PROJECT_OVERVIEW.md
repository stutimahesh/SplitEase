# SplitEase — Project Overview

This document explains what SplitEase does, how it's built, and how every
piece connects — in enough depth to walk through in an interview.

---

## 1. What it does (in one paragraph)

SplitEase is a Splitwise-style expense splitter. Users sign up, create a
group with friends, and log shared expenses (either split equally or with
a custom amount per person). SplitEase then computes each person's **net
balance** in the group, and a **settle-up** view that shows the *minimum
number of payments* needed to clear every debt — instead of everyone
paying everyone back individually.

---

## 2. Tech stack and why

| Layer | Choice | Why |
|---|---|---|
| Backend | Flask (Python) | Lightweight, explicit routing, easy to reason about — no hidden magic |
| ORM / DB | Flask-SQLAlchemy + SQLite | SQLite needs no separate server to install (keeps the project simple to run); SQLAlchemy is swappable to Postgres/MySQL via `DATABASE_URL` with zero code changes |
| Auth | Flask-JWT-Extended | Stateless tokens — no server-side session store needed |
| Frontend | React (Vite) | Fast dev server, component-based UI, industry standard |
| Routing | React Router | Client-side navigation between pages |
| HTTP client | Axios | Simple interceptor support for attaching the JWT to every request |

No Docker, no CI/CD, no cloud deployment — everything runs with `python run.py`
and `npm run dev`.

---

## 3. Project structure

```
SplitEase/
├── backend/
│   ├── app/
│   │   ├── __init__.py      # Flask app factory — wires everything together
│   │   ├── config.py        # reads SECRET_KEY / DATABASE_URL / JWT key from env
│   │   ├── extensions.py    # shared db (SQLAlchemy) and jwt instances
│   │   ├── models.py        # User, Group, GroupMember, Expense, ExpenseSplit
│   │   ├── auth.py          # /api/auth/register, /login, /me
│   │   ├── groups.py        # /api/groups ... (create/list/detail/add member)
│   │   ├── expenses.py      # /api/groups/<id>/expenses (add/list)
│   │   ├── balances.py      # balance calculation + settle-up algorithm
│   │   └── utils.py         # require_member() — shared access-control check
│   ├── tests/test_balances.py
│   ├── seed.py               # populates sample data for demos
│   └── run.py                 # entrypoint: `python run.py`
└── frontend/
    └── src/
        ├── api/client.js              # axios instance, attaches JWT to every request
        ├── context/AuthContext.jsx    # holds logged-in user, login()/logout()
        ├── pages/
        │   ├── Login.jsx / Signup.jsx
        │   ├── Groups.jsx             # list + create groups
        │   └── GroupDetail.jsx        # members, balances, settle-up, expenses
        ├── components/
        │   ├── ExpenseForm.jsx        # add expense, equal/custom split toggle
        │   ├── BalancesView.jsx       # renders net balance per member
        │   └── SettleUp.jsx           # renders minimal payment list
        └── App.jsx                    # routes + auth guard
```

---

## 4. The data model (the part you can draw on a whiteboard)

Five tables:

```
User            Group             GroupMember          Expense              ExpenseSplit
--------        --------          -----------------     ----------------     ----------------
id              id                id                    id                   id
name            name              group_id  -> Group     group_id -> Group    expense_id -> Expense
email (unique)  created_by->User  user_id   -> User       paid_by  -> User     user_id -> User
password_hash   created_at        joined_at              amount               amount_owed
created_at                                                description
                                                           created_at
```

- **GroupMember** is the join table for the many-to-many between `User` and
  `Group` — it's what "membership" means, and every group route checks it.
- **Expense** records *who paid* and *how much*, in total.
- **ExpenseSplit** records, per expense, *how that amount is divided* across
  members. One `Expense` has many `ExpenseSplit` rows (one per participant).

This split between `Expense` (the payment) and `ExpenseSplit` (the
division) is the key design decision — it's what makes both equal splits
and custom splits representable with the same schema, and it's what makes
the balance calculation below a couple of lines of code.

---

## 5. Balance calculation — the core logic

For each member of a group:

```
net balance = (total amount they paid across all expenses)
            − (total of their own split shares across all expenses)
```

Implemented in `backend/app/balances.py::_calculate_net_balances`:

```python
balances = {member_id: 0.0 for member in group}
for expense in group.expenses:
    balances[expense.paid_by] += expense.amount        # they fronted this much
    for split in expense.splits:
        balances[split.user_id] -= split.amount_owed    # they owe their share
```

**Worked example** (this is literally the seed data): Alice pays ₹3000 for a
hotel, split equally 3 ways (₹1000 each).

- Alice: paid 3000, owes herself 1000 → net = **+2000** (the group owes her ₹2000)
- Bob: paid 0, owes 1000 → net = **−1000** (he owes ₹1000)
- Carol: paid 0, owes 1000 → net = **−1000**

Check: 2000 − 1000 − 1000 = 0. Balances always sum to zero — every rupee
paid is owed by someone.

A **positive** balance means *the group owes them*; **negative** means
*they owe the group*.

---

## 6. Settle-up algorithm — the one worth explaining in depth

Naively, you could have every debtor pay every creditor for every expense
they were part of — that's a lot of transactions. Instead, once you have
each person's **single net balance** (from step 5), you only need to zero
those numbers out, and there's a classic greedy algorithm to do it in the
minimum number of payments:

```python
def _minimize_transactions(net_balances):
    creditors = sorted([uid, amt] for amt > 0, descending by amount)
    debtors   = sorted([uid, amt] for amt < 0, descending by abs(amount))

    transactions = []
    while there are debtors and creditors left:
        take the largest debtor and the largest creditor
        settle = min(debtor's remaining debt, creditor's remaining credit)
        record a payment: debtor -> creditor, amount = settle
        reduce both by `settle`
        drop whichever (or both) hit zero
    return transactions
```

**Why greedy works here:** every payment fully clears at least one person's
balance (whichever side was smaller). With N people, at most N−1 payments
are ever needed to clear everyone — you can prove this by induction: each
step removes one person from the problem, so it terminates in ≤ N−1 steps.

**Worked example continued:** balances are Alice +2000, Bob −1000, Carol −1000.
- Largest creditor: Alice (+2000). Largest debtor: Bob or Carol (−1000, tie).
- Settle Bob → Alice ₹1000. Bob is now 0, drops out.
- Settle Carol → Alice ₹1000. Both drop out.
- Result: **2 payments** instead of settling per-expense.

This is implemented and unit-tested in `backend/tests/test_balances.py`
(4 tests, including one that asserts the transactions always sum back to
the original balances — a correctness check, not just an example check).

---

## 7. Request flow — walking through "Alice adds an expense"

1. **Frontend** (`ExpenseForm.jsx`): Alice fills in description, amount,
   who paid, and picks equal or custom split. On submit, it `POST`s to
   `/api/groups/<id>/expenses` via the shared `api` axios instance.
2. **`api/client.js`** intercepts the request and attaches
   `Authorization: Bearer <token>` from `localStorage` automatically —
   every page doesn't need to think about auth headers.
3. **Backend** (`expenses.py::add_expense`):
   - `@jwt_required()` decodes the token → gets `user_id`.
   - `require_member(group_id, user_id)` (from `utils.py`) checks a
     `GroupMember` row exists — if not, aborts with 403. This same helper
     is reused by `groups.py` and `balances.py`, so "can this user see this
     group's data" is enforced in exactly one place.
   - If no custom `splits` were sent, it divides `amount` equally among all
     `GroupMember` rows for that group. If custom splits were sent, it
     validates they sum to the total amount (else 400).
   - Creates one `Expense` row + one `ExpenseSplit` row per participant.
4. **Frontend** re-fetches expenses, balances, and settle-up (`refreshAll()`
   in `GroupDetail.jsx`) so the UI reflects the new numbers immediately.

## 8. Auth flow

- `POST /api/auth/register` — hashes the password with Werkzeug's
  `generate_password_hash` (never stored in plaintext), creates the user,
  returns a JWT.
- `POST /api/auth/login` — verifies with `check_password_hash`, returns a JWT.
- The JWT's identity is the user's `id` (as a string, per Flask-JWT-Extended's
  convention). Every protected route decodes it with `get_jwt_identity()`.
- **Frontend** stores the token in `localStorage` and restores the session
  on page load by calling `GET /api/auth/me` (see `AuthContext.jsx`) — this
  is why refreshing the page doesn't log you out.

---

## 9. Likely interview questions and how to answer them

- **"Why net balance instead of tracking every pairwise debt?"**
  Because pairwise tracking grows as O(n²) relationships and doesn't
  compose — you'd have to manually cancel out chains of debt (A owes B,
  B owes C). Reducing everyone to one number per group makes settlement a
  simple greedy matching problem instead.

- **"What happens if custom splits don't add up to the total?"**
  The backend rejects it with a 400 before writing anything to the DB
  (`expenses.py`) — validation happens server-side, not just in the form.

- **"How do you stop User A from seeing User B's private group?"**
  `require_member()` — every group-scoped route checks a `GroupMember` row
  exists for `(group_id, user_id)` before returning any data, and aborts
  with 403 otherwise.

- **"Why SQLite instead of Postgres?"**
  For local development simplicity — no separate DB server to install.
  `SQLALCHEMY_DATABASE_URI` reads from `DATABASE_URL`, so switching to
  Postgres in production is a config change, not a code change.

- **"What would you add with more time?"**
  Multi-currency support, expense editing/deletion (currently append-only),
  and recording *when* a settle-up payment actually happened (right now
  settle-up is a computed suggestion, not a recorded transaction).
