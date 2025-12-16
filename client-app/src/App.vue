<template>
  <ErrorBoundary>
    <router-view />
    <ToastContainer />
    <MiniWalletWidget />
    <ChatWidget />
  </ErrorBoundary>
</template>

<script setup>
import ErrorBoundary from './components/shared/ErrorBoundary.vue';
import ToastContainer from './components/shared/ToastContainer.vue';
import MiniWalletWidget from './components/personal/shared/MiniWalletWidget.vue';
import ChatWidget from './components/support/ChatWidget.vue';
</script>
