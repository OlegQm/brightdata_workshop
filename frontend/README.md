# Frontend

Vue 3 + Vite application on port `5173`.

Responsibilities:

- renders the CZ/SK hotel map with MapLibre and PMTiles;
- lists and selects hotels from the backend API;
- exposes the settings screen at `/#settings`;
- opens the HotelFinder chat and consumes backend SSE responses.

Important files:

- `src/App.vue` - main application state, map setup, API calls and chat wiring.
- `src/components/` - reusable UI panels.
- `src/style.css` - global application styling.
- `vite.config.js` - Vite dev server config.
- `Dockerfile.dev` - development container used by compose.

The backend URL comes from `VITE_BACKEND_URL`; compose sets it to
`http://localhost:8002`.
