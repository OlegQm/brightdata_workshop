<template>
  <article v-if="hotel" class="detail-panel">
    <div class="detail-header">
      <div>
        <p>{{ hotel.city }}, {{ hotel.country }}</p>
        <h2>{{ hotel.name }}</h2>
      </div>
      <button class="icon-button" aria-label="Close details" @click="$emit('close')">×</button>
    </div>
    <dl>
      <div>
        <dt>Address</dt>
        <dd>{{ hotel.address }}</dd>
      </div>
      <div v-if="hotel.phone">
        <dt>Phone</dt>
        <dd>{{ hotel.phone }}</dd>
      </div>
      <div v-if="hotel.email">
        <dt>Email</dt>
        <dd>{{ hotel.email }}</dd>
      </div>
    </dl>
    <p class="description">{{ hotel.description }}</p>
    <div class="actions">
      <a v-if="hotel.website" :href="hotel.website" target="_blank" rel="noreferrer">Website</a>
      <a :href="hotel.source_url" target="_blank" rel="noreferrer">BrightData source</a>
    </div>
  </article>
</template>

<script setup>
defineProps({
  hotel: { type: Object, default: null },
});

defineEmits(["close"]);
</script>
