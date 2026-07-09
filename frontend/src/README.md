# Frontend Source

Main Vue source tree.

Files:

- `main.js` - creates and mounts the Vue application.
- `App.vue` - top-level map, settings and chat orchestration.
- `style.css` - global layout and component styling.
- `components/` - UI panels used by `App.vue`.

Keep data fetching and page-level state in `App.vue` unless a component becomes
large enough to justify moving behavior down.
