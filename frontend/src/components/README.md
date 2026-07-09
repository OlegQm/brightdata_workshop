# Frontend Components

Reusable Vue components for the map UI.

Components:

- `MapSidebar.vue` - search/filter sidebar and hotel list.
- `HotelDetailPanel.vue` - selected hotel details.
- `ChatPanel.vue` - HotelFinder chat shell and message input.
- `SettingsPage.vue` - refresh status and BrightData refresh trigger.

Components receive state through props and report user actions with emits. The
top-level API calls and map mutation logic stay in `App.vue`.
