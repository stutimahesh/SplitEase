# SplitEase frontend

A React (Vite) single-page app for the SplitEase expense splitter.

## Setup

```bash
cd frontend
npm install
```

## Run

```bash
npm run dev
```

The app runs at `http://localhost:5173` and proxies `/api` requests to the
Flask backend at `http://localhost:5000` (see `vite.config.js`). Make sure the
backend is running first — see [`../backend/README.md`](../backend/README.md).

## Build for production

```bash
npm run build
```

## Pages

- `/login`, `/signup` — auth
- `/groups` — list of groups you belong to, create a new group
- `/groups/:groupId` — group detail: members, balances, settle-up, add/view expenses

Auth is JWT-based: the token is stored in `localStorage` and attached to every
API request via an axios interceptor (see `src/api/client.js`).
