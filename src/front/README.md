# Tapin Frontend

React + Vite SPA for the Tapin marketplace experience.

## Prerequisites

- Node.js 20+ (npm ships with Node)
- Backend API from `src/backend` running locally or remotely

## Quick Start

> `package.json` lives at the repository root (`Tapin_Correct`). Run all npm commands from there; Vite already points at `src/front/src`.

```bash
cd /path/to/Tapin_Correct
npm install             # install Vite/React deps
npm run dev             # start the frontend on http://localhost:5173
```

For network testing you can pass `npm run dev -- --host 0.0.0.0 --port 4173`.

## Available Scripts

- `npm run dev` – Vite dev server with HMR
- `npm run build` – production build to `dist/`
- `npm run preview` – serve the production build locally
- `npm run test` – run Vitest/JSDOM tests (if present)

## Project Structure

```
src/front/
├── index.html          # Vite entry
├── public/             # Static assets
└── src/
    ├── assets/
    ├── components/
    ├── pages/
    ├── test/
    ├── App.jsx
    └── main.jsx
```

## Backend Integration

Frontend fetches from the API defined by `VITE_API_URL` (falls back to `http://127.0.0.1:5000`). Configure `.env` at the repo root:

```env
VITE_API_URL=http://127.0.0.1:5000
```

Restart `npm run dev` after changing env vars. Ensure the Flask backend is running before using features such as auth, listings, and reviews.

## Deployment

```
npm run build
npm run preview   # optional sanity check
```

Files land in `/dist` and are served by `src/app.py` in production. Copy that directory to your hosting target or let Flask serve it as configured in this repo.

## Contributing

1. Add shared UI in `src/components/`; route-level screens in `src/pages/`.
2. Keep `README.md` updated when setup or scripts change.
3. Co-locate tests under `src/test` or alongside components with `.test.jsx` files.

Happy building!
