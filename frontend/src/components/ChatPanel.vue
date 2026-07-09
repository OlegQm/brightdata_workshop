<template>
  <aside class="chat-panel" :class="{ open: chatOpen, minimized: chatMinimized }">
    <header class="panel-header chat-panel-header" @click.self="chatMinimized && $emit('restore-chat')">
      <div class="brand" style="cursor:pointer" @click="chatMinimized && $emit('restore-chat')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <span>Hotel<strong>Finder</strong></span>
      </div>
      <div class="panel-header-actions">
        <button class="panel-icon-btn chat-minimize-btn" @click="$emit('minimize-chat')" aria-label="Minimize chat">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="collapse-chevron" :class="{ flipped: !chatMinimized }"><polyline points="18 15 12 9 6 15"/></svg>
        </button>
        <button class="panel-icon-btn" @click="$emit('close-chat')" aria-label="Close chat">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </header>

    <div class="chat-messages" ref="messagesEl">
      <div v-for="msg in chatMessages" :key="msg.id" class="chat-msg" :class="msg.role">
        <div class="chat-bubble" :class="{ 'chat-typing': msg.thinking && !msg.content }">
          <template v-if="msg.thinking && !msg.content">
            <span></span><span></span><span></span>
          </template>
          <template v-else>{{ msg.content }}</template>
        </div>
      </div>
      <div v-if="chatLoading" class="chat-msg bot">
        <div class="chat-bubble chat-typing">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <div class="chat-input-row">
      <input
        :value="chatInput"
        @input="$emit('update:chat-input', $event.target.value)"
        @keydown.enter.prevent="$emit('send-chat-message')"
        placeholder="Ask about hotels..."
        :disabled="chatLoading"
        autocomplete="off"
      />
      <button class="chat-send-btn" @click="$emit('send-chat-message')" :disabled="chatLoading || !chatInput.trim()" aria-label="Send">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  chatOpen: { type: Boolean, required: true },
  chatMinimized: { type: Boolean, required: true },
  chatMessages: { type: Array, required: true },
  chatLoading: { type: Boolean, required: true },
  chatInput: { type: String, required: true },
  scrollKey: { type: Number, required: true },
});

defineEmits([
  "update:chat-input",
  "restore-chat",
  "minimize-chat",
  "close-chat",
  "send-chat-message",
]);

const messagesEl = ref(null);

watch(
  () => props.scrollKey,
  () => {
    requestAnimationFrame(() => {
      if (messagesEl.value) {
        messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
      }
    });
  }
);
</script>
