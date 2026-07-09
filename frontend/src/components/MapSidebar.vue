<template>
  <aside class="sidebar">
    <header class="sidebar-header">
      <div>
        <p class="eyebrow">OpenStreetMap CZ/SK</p>
        <h1>Hotels</h1>
      </div>
      <div class="header-tools">
        <a class="settings-link" href="#settings" aria-label="Open settings">⚙</a>
        <span class="count">{{ hotels.length }}</span>
      </div>
    </header>

    <div class="toolbar">
      <label class="search">
        <span>Search</span>
        <input :value="query" type="search" placeholder="City, hotel, address" @input="$emit('update:query', $event.target.value)" />
      </label>
      <div class="segments" aria-label="Country filter">
        <button :class="{ active: country === '' }" @click="$emit('update:country', '')">All</button>
        <button :class="{ active: country === 'Slovakia' }" @click="$emit('update:country', 'Slovakia')">SK</button>
        <button :class="{ active: country === 'Czechia' }" @click="$emit('update:country', 'Czechia')">CZ</button>
      </div>
    </div>

    <section class="hotel-list" aria-label="Hotels">
      <button
        v-for="hotel in hotels"
        :key="hotel.id"
        class="hotel-row"
        :class="{ active: selectedHotel?.id === hotel.id }"
        @click="$emit('select-hotel', hotel)"
      >
        <span class="pin-dot" :class="hotel.country === 'Slovakia' ? 'sk' : 'cz'"></span>
        <span class="hotel-row-main">
          <strong>{{ hotel.name }}</strong>
          <small>{{ hotel.city }} · {{ hotel.rating || "Hotel" }}</small>
        </span>
      </button>
    </section>
  </aside>
</template>

<script setup>
defineProps({
  hotels: { type: Array, required: true },
  selectedHotel: { type: Object, default: null },
  query: { type: String, required: true },
  country: { type: String, required: true },
});

defineEmits(["update:query", "update:country", "select-hotel"]);
</script>
