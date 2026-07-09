<template>
  <main class="settings-shell">
    <aside class="settings-panel">
      <header class="settings-brand">
        <div>
          <p class="settings-eyebrow">Data operations</p>
          <h1>Settings</h1>
        </div>
      </header>
      <nav class="settings-nav">
        <a href="#">Map</a>
        <a class="active" href="#settings">BrightData refresh</a>
      </nav>
      <section class="settings-card compact">
        <p>Total hotels</p>
        <strong>{{ refreshStatus?.total ?? totalHotels }}</strong>
      </section>
      <section class="settings-card compact">
        <p>Refreshed</p>
        <strong>{{ refreshStatus?.refreshed ?? 0 }}</strong>
      </section>
    </aside>

    <section class="settings-workspace">
      <header class="settings-header">
        <div>
          <p class="settings-eyebrow">BrightData MCP</p>
          <h1>Live hotel updates</h1>
        </div>
        <button class="settings-ghost" @click="$emit('load-refresh-status')">Refresh status</button>
      </header>

      <p v-if="refreshError" class="settings-error">{{ refreshError }}</p>

      <section class="settings-grid">
        <article class="settings-card">
          <div class="card-title-row">
            <div>
              <p class="settings-eyebrow">Token</p>
              <h2>{{ refreshStatus?.token_configured ? "Configured" : "Missing" }}</h2>
            </div>
            <span class="status-pill" :class="{ ok: refreshStatus?.token_configured }">
              {{ refreshStatus?.token_configured ? "Ready" : "Needs .env" }}
            </span>
          </div>
          <p class="muted">
            Backend reads <code>BRIGHTDATA_API_TOKEN</code> from <code>.env</code>. The token is never sent to the browser.
          </p>
        </article>

        <article class="settings-card">
          <div class="card-title-row">
            <div>
              <p class="settings-eyebrow">Refresh</p>
              <h2>Update hotel records</h2>
            </div>
          </div>
          <p class="muted">
            Scrapes current hotel source pages through BrightData MCP, updates contacts/source payloads, and recalculates pgvector embeddings in Postgres.
          </p>
          <button class="settings-primary" :disabled="refreshing || !refreshStatus?.token_configured" @click="$emit('refresh-hotels')">
            <span v-if="refreshing" class="settings-spinner"></span>
            {{ refreshing ? "Updating" : "Update with BrightData" }}
          </button>
        </article>

        <article class="settings-card wide">
          <div class="card-title-row">
            <div>
              <p class="settings-eyebrow">Last result</p>
              <h2>{{ refreshResult?.message || "No refresh in this session" }}</h2>
            </div>
          </div>
          <dl class="settings-metrics">
            <div>
              <dt>Updated</dt>
              <dd>{{ refreshResult?.updated ?? "—" }}</dd>
            </div>
            <div>
              <dt>Failed</dt>
              <dd>{{ refreshResult?.failed ?? "—" }}</dd>
            </div>
            <div>
              <dt>Last refreshed</dt>
              <dd>{{ refreshStatus?.last_refreshed_at || "—" }}</dd>
            </div>
          </dl>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup>
defineProps({
  refreshStatus: { type: Object, default: null },
  refreshResult: { type: Object, default: null },
  refreshError: { type: String, default: "" },
  refreshing: { type: Boolean, required: true },
  totalHotels: { type: Number, required: true },
});

defineEmits(["load-refresh-status", "refresh-hotels"]);
</script>
