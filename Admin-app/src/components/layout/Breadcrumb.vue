<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const breadcrumbs = computed(() => {
  const paths = route.path.split('/').filter(Boolean);
  const crumbs = [{ name: 'Trang chủ', path: '/dashboard' }];

  let currentPath = '';
  paths.forEach((path, index) => {
    currentPath += `/${path}`;
    const name = path
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    crumbs.push({
      name,
      path: currentPath,
    });
  });

  return crumbs;
});
</script>

<template>
  <nav class="flex items-center gap-2 text-sm">
    <template v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
      <router-link
        :to="crumb.path"
        :class="[
          'transition-colors',
          index === breadcrumbs.length - 1
            ? 'text-white font-medium'
            : 'text-white/60 hover:text-white',
        ]"
      >
        {{ crumb.name }}
      </router-link>
      <i
        v-if="index < breadcrumbs.length - 1"
        class="fas fa-chevron-right text-white/40 text-xs mx-1"
      ></i>
    </template>
  </nav>
</template>

