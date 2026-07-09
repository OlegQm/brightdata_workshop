<template>
  <main v-show="currentPage === 'map'" class="app-shell">
    <MapSidebar
      v-model:query="query"
      v-model:country="country"
      :hotels="filteredHotels"
      :selected-hotel="selectedHotel"
      @select-hotel="selectHotel($event, true)"
    />

    <section class="map-stage">
      <div ref="mapEl" class="map"></div>
      <div v-if="loading" class="status-panel">Loading hotels and map data...</div>
      <div v-if="error" class="status-panel error">{{ error }}</div>

      <HotelDetailPanel :hotel="selectedHotel" @close="selectedHotel = null" />

      <button class="chat-toggle" v-show="!chatOpen" @click="openChat" aria-label="Open hotel finder">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </button>
      <div v-if="chatOpen" class="chat-backdrop" @click="closeChat"></div>
      <ChatPanel
        v-model:chat-input="chatInput"
        :chat-open="chatOpen"
        :chat-minimized="chatMinimized"
        :chat-messages="chatMessages"
        :chat-loading="chatLoading"
        :scroll-key="chatScrollKey"
        @restore-chat="chatMinimized = false"
        @minimize-chat="chatMinimized = !chatMinimized"
        @close-chat="closeChat"
        @send-chat-message="sendChatMessage"
      />
    </section>
  </main>

  <SettingsPage
    v-show="currentPage === 'settings'"
    :refresh-status="refreshStatus"
    :refresh-result="refreshResult"
    :refresh-error="refreshError"
    :refreshing="refreshing"
    :total-hotels="filteredHotels.length"
    @load-refresh-status="loadRefreshStatus"
    @refresh-hotels="refreshHotels"
  />
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import maplibregl from "maplibre-gl";
import { layers, namedFlavor } from "@protomaps/basemaps";
import { Protocol } from "pmtiles";
import ChatPanel from "./components/ChatPanel.vue";
import HotelDetailPanel from "./components/HotelDetailPanel.vue";
import MapSidebar from "./components/MapSidebar.vue";
import SettingsPage from "./components/SettingsPage.vue";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8002";
const PMTILES_URL = `${BACKEND_URL}/data/czsk.pmtiles`;
const BOUNDARY_URL = `${BACKEND_URL}/data/czsk_boundary.geojson`;

const mapEl = ref(null);
const hotels = ref([]);
const selectedHotel = ref(null);
const query = ref("");
const country = ref("");
const loading = ref(true);
const error = ref("");
const currentPage = ref(window.location.hash === "#settings" ? "settings" : "map");
const refreshStatus = ref(null);
const refreshResult = ref(null);
const refreshError = ref("");
const refreshing = ref(false);
const chatOpen = ref(false);
const chatMinimized = ref(false);
const chatMessages = ref([
  {
    id: 1,
    role: "bot",
    content: "Ask me to filter hotels by city, country, rating, contact details, or any phrase from the description.",
  },
]);
const chatInput = ref("");
const chatLoading = ref(false);
const chatScrollKey = ref(0);
const chatSessionId = ref(null);

let map;
let protocol;
let domMarkers = [];
let chatMsgIdCounter = 2;
let chatAbortController = null;

const filteredHotels = computed(() => hotels.value);

function hotelFeatureCollection(items) {
  return {
    type: "FeatureCollection",
    features: items.map((hotel) => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [hotel.longitude, hotel.latitude] },
      properties: {
        id: hotel.id,
        name: hotel.name,
        city: hotel.city,
        country: hotel.country,
        rating: hotel.rating || "",
      },
    })),
  };
}

function selectHotel(hotel, fly = false) {
  selectedHotel.value = hotel;
  if (fly && map) {
    map.flyTo({ center: [hotel.longitude, hotel.latitude], zoom: 13.5, essential: true });
  }
}

function syncHotelLayer() {
  const source = map?.getSource("hotels");
  if (source) source.setData(hotelFeatureCollection(filteredHotels.value));
  syncDomMarkers();
}

function syncDomMarkers() {
  if (!map) return;
  for (const marker of domMarkers) marker.remove();
  domMarkers = filteredHotels.value.map((hotel) => {
    const el = document.createElement("button");
    el.type = "button";
    el.className = `hotel-marker ${hotel.country === "Slovakia" ? "sk" : "cz"}`;
    el.setAttribute("aria-label", hotel.name);
    el.title = hotel.name;
    el.addEventListener("click", () => selectHotel(hotel));
    return new maplibregl.Marker({ element: el, anchor: "center" })
      .setLngLat([hotel.longitude, hotel.latitude])
      .addTo(map);
  });
}

function fitHotels(items) {
  if (!map || !items.length) return;
  const lngs = items.map((hotel) => hotel.longitude);
  const lats = items.map((hotel) => hotel.latitude);
  map.fitBounds(
    [[Math.min(...lngs), Math.min(...lats)], [Math.max(...lngs), Math.max(...lats)]],
    { padding: 80, maxZoom: 13.5 }
  );
}

function applyChatHotels(items) {
  if (!Array.isArray(items)) return;
  hotels.value = items;
  selectedHotel.value = null;
  syncHotelLayer();
  fitHotels(items);
}

function scrollChatToBottom() {
  chatScrollKey.value += 1;
}

function openChat() {
  chatOpen.value = true;
  chatMinimized.value = false;
  scrollChatToBottom();
}

async function closeChat() {
  chatOpen.value = false;
  chatMinimized.value = false;
  if (chatAbortController) {
    chatAbortController.abort();
    chatAbortController = null;
  }
  if (chatSessionId.value) {
    await fetch(`${BACKEND_URL}/api/chat/${chatSessionId.value}`, { method: "DELETE" }).catch(() => {});
    chatSessionId.value = null;
  }
}

function handleChatPayload(payload, botMsg, state) {
  if (payload.session_id) {
    chatSessionId.value = payload.session_id;
    return;
  }
  if (payload.discard) {
    botMsg.content = "";
    botMsg.thinking = true;
    if (!state.botMsgAdded) {
      chatLoading.value = false;
      chatMessages.value.push(botMsg);
      state.botMsgAdded = true;
    }
    scrollChatToBottom();
    return;
  }
  if (payload.status === "thinking" && !state.botMsgAdded) {
    chatLoading.value = false;
    botMsg.thinking = true;
    chatMessages.value.push(botMsg);
    state.botMsgAdded = true;
    scrollChatToBottom();
    return;
  }
  if (payload.token) {
    if (!state.botMsgAdded) {
      chatLoading.value = false;
      chatMessages.value.push(botMsg);
      state.botMsgAdded = true;
    }
    botMsg.thinking = false;
    botMsg.content += payload.token;
    scrollChatToBottom();
    return;
  }
  if ("hotels" in payload && payload.hotels) {
    applyChatHotels(payload.hotels);
  }
}

async function sendChatMessage() {
  const text = chatInput.value.trim();
  if (!text || chatLoading.value) return;

  chatInput.value = "";
  chatMessages.value.push({ id: chatMsgIdCounter++, role: "user", content: text });
  chatLoading.value = true;
  await nextTick();
  scrollChatToBottom();

  const botMsg = reactive({ id: chatMsgIdCounter++, role: "bot", content: "", thinking: false });
  const state = { botMsgAdded: false };
  const controller = new AbortController();
  chatAbortController = controller;

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({ session_id: chatSessionId.value, message: text }),
    });
    if (!response.ok || !response.body) {
      throw new Error(`Chat API returned ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      if (controller.signal.aborted) return;
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const raw = line.slice(5).trim();
        if (!raw) continue;
        try {
          handleChatPayload(JSON.parse(raw), botMsg, state);
          await nextTick();
        } catch {
          // Ignore malformed SSE chunks.
        }
      }
    }
  } catch (err) {
    if (err?.name === "AbortError") return;
    const message = err instanceof Error ? err.message : "Connection error. Please try again.";
    if (state.botMsgAdded) {
      botMsg.thinking = false;
      botMsg.content = message;
    } else {
      chatMessages.value.push({ id: chatMsgIdCounter++, role: "bot", content: message });
    }
  } finally {
    if (chatAbortController === controller) {
      chatAbortController = null;
    }
    chatLoading.value = false;
    await nextTick();
    scrollChatToBottom();
  }
}

async function loadHotels() {
  const params = new URLSearchParams();
  if (query.value.trim()) params.set("q", query.value.trim());
  if (country.value) params.set("country", country.value);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${BACKEND_URL}/api/hotels${suffix}`);
  if (!response.ok) throw new Error(`Hotels API returned ${response.status}`);
  hotels.value = await response.json();
}

async function api(path, options = {}) {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadRefreshStatus() {
  refreshError.value = "";
  try {
    refreshStatus.value = await api("/api/hotels/refresh/status");
  } catch (err) {
    refreshError.value = err instanceof Error ? err.message : String(err);
  }
}

async function refreshHotels() {
  if (refreshing.value) return;
  refreshing.value = true;
  refreshError.value = "";
  try {
    refreshResult.value = await api("/api/hotels/refresh", { method: "POST" });
    await Promise.all([loadHotels(), loadRefreshStatus()]);
  } catch (err) {
    refreshError.value = err instanceof Error ? err.message : String(err);
  } finally {
    refreshing.value = false;
  }
}

async function initMap() {
  protocol = new Protocol();
  maplibregl.addProtocol("pmtiles", protocol.tile);

  map = new maplibregl.Map({
    container: mapEl.value,
    style: {
      version: 8,
      glyphs: "https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf",
      sprite: "https://protomaps.github.io/basemaps-assets/sprites/v4/light",
      sources: {
        protomaps: {
          type: "vector",
          url: `pmtiles://${PMTILES_URL}`,
          attribution: '<a href="https://openstreetmap.org">OpenStreetMap</a>',
        },
      },
      layers: layers("protomaps", namedFlavor("light"), { lang: "en" }),
    },
    center: [17.25, 49.35],
    zoom: 6.45,
    projection: "mercator",
    fadeDuration: 0,
    validateStyle: false,
  });

  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");

  map.once("load", async () => {
    const boundary = await fetch(BOUNDARY_URL).then((response) => response.json());
    map.addSource("czsk-boundary", { type: "geojson", data: boundary });
    map.addLayer({
      id: "czsk-boundary-fill",
      type: "fill",
      source: "czsk-boundary",
      paint: { "fill-color": "#16a34a", "fill-opacity": 0.045 },
    });
    map.addLayer({
      id: "czsk-boundary-line",
      type: "line",
      source: "czsk-boundary",
      paint: { "line-color": "#166534", "line-width": 1.5, "line-opacity": 0.75 },
    });

    map.addSource("hotels", { type: "geojson", data: hotelFeatureCollection(filteredHotels.value) });
    map.addLayer({
      id: "hotel-points",
      type: "circle",
      source: "hotels",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 5, 5, 10, 8, 14, 12],
        "circle-color": ["match", ["get", "country"], "Slovakia", "#0f766e", "Czechia", "#b45309", "#374151"],
        "circle-stroke-color": "#ffffff",
        "circle-stroke-width": 2,
        "circle-opacity": 0.94,
      },
    });
    map.addLayer({
      id: "hotel-labels",
      type: "symbol",
      source: "hotels",
      minzoom: 7,
      layout: {
        "text-field": ["get", "name"],
        "text-size": 12,
        "text-anchor": "top",
        "text-offset": [0, 1.1],
        "text-allow-overlap": false,
      },
      paint: {
        "text-color": "#172554",
        "text-halo-color": "#ffffff",
        "text-halo-width": 1.4,
      },
    });
    syncDomMarkers();

    map.on("click", "hotel-points", (event) => {
      const id = event.features?.[0]?.properties?.id;
      const hotel = hotels.value.find((item) => item.id === id);
      if (hotel) selectHotel(hotel);
    });
    map.on("mouseenter", "hotel-points", () => { map.getCanvas().style.cursor = "pointer"; });
    map.on("mouseleave", "hotel-points", () => { map.getCanvas().style.cursor = ""; });
  });
}

watch(filteredHotels, () => {
  syncHotelLayer();
  if (selectedHotel.value && !filteredHotels.value.some((hotel) => hotel.id === selectedHotel.value.id)) {
    selectedHotel.value = null;
  }
});

let searchTimer;
watch([query, country], () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(async () => {
    try {
      await loadHotels();
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err);
    }
  }, 180);
});

function onHashChange() {
  currentPage.value = window.location.hash === "#settings" ? "settings" : "map";
  if (currentPage.value === "map" && map) {
    window.setTimeout(() => map.resize(), 50);
  }
}

onMounted(async () => {
  try {
    window.addEventListener("hashchange", onHashChange);
    await loadHotels();
    await loadRefreshStatus();
    await initMap();
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("hashchange", onHashChange);
  window.clearTimeout(searchTimer);
  if (chatAbortController) chatAbortController.abort();
  for (const marker of domMarkers) marker.remove();
  domMarkers = [];
  if (map) map.remove();
  if (protocol) maplibregl.removeProtocol("pmtiles");
});
</script>
