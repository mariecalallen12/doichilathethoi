<template>
  <div class="flex flex-col lg:flex-row gap-8">
    <!-- Table of Contents -->
    <nav
      v-if="toc.length > 0"
      class="lg:w-64 flex-shrink-0"
      aria-label="Mục lục"
    >
      <div class="sticky top-8 bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
        <h2 class="text-lg font-bold text-white mb-4">Mục Lục</h2>
        <ul class="space-y-2">
          <li
            v-for="item in toc"
            :key="item.id"
            class="text-sm"
          >
            <a
              :href="`#${item.id}`"
              class="text-gray-400 hover:text-purple-400 transition-colors block py-1"
              :class="{ 'text-purple-400 font-semibold': activeSection === item.id }"
              @click.prevent="scrollToSection(item.id)"
            >
              {{ item.title }}
            </a>
            <ul v-if="item.children && item.children.length > 0" class="ml-4 mt-1 space-y-1">
              <li
                v-for="child in item.children"
                :key="child.id"
              >
                <a
                  :href="`#${child.id}`"
                  class="text-gray-500 hover:text-purple-400 transition-colors text-xs block py-1"
                  :class="{ 'text-purple-400': activeSection === child.id }"
                  @click.prevent="scrollToSection(child.id)"
                >
                  {{ child.title }}
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Content -->
    <div class="flex-1">
      <div
        ref="contentRef"
        class="prose prose-invert max-w-none text-gray-300 legal-content"
        v-html="formattedContent"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  content: {
    type: String,
    default: ''
  }
});

const contentRef = ref(null);
const toc = ref([]);
const activeSection = ref('');

const formattedContent = computed(() => {
  if (!props.content) return '';
  
  // Parse content and extract headings for TOC
  const parser = new DOMParser();
  const doc = parser.parseFromString(props.content, 'text/html');
  const headings = doc.querySelectorAll('h1, h2, h3');
  
  toc.value = [];
  headings.forEach((heading, index) => {
    const id = `section-${index}`;
    heading.id = id;
    heading.setAttribute('tabindex', '-1');
    
    const level = parseInt(heading.tagName.charAt(1));
    const title = heading.textContent.trim();
    
    if (level === 1) {
      toc.value.push({ id, title, level, children: [] });
    } else if (level === 2 && toc.value.length > 0) {
      const lastParent = toc.value[toc.value.length - 1];
      if (!lastParent.children) lastParent.children = [];
      lastParent.children.push({ id, title, level });
    }
  });
  
  return doc.body.innerHTML;
});

const scrollToSection = (id) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    activeSection.value = id;
    // Update URL without reload
    history.pushState(null, '', `#${id}`);
  }
};

const updateActiveSection = () => {
  if (!contentRef.value) return;
  
  const headings = contentRef.value.querySelectorAll('h1, h2, h3');
  const scrollPosition = window.scrollY + 100;
  
  for (let i = headings.length - 1; i >= 0; i--) {
    const heading = headings[i];
    const rect = heading.getBoundingClientRect();
    const top = rect.top + window.scrollY;
    
    if (scrollPosition >= top) {
      activeSection.value = heading.id;
      break;
    }
  }
};

onMounted(() => {
  // Handle initial hash
  if (window.location.hash) {
    const id = window.location.hash.substring(1);
    setTimeout(() => scrollToSection(id), 100);
  }
  
  // Update active section on scroll
  window.addEventListener('scroll', updateActiveSection);
  updateActiveSection();
});

onUnmounted(() => {
  window.removeEventListener('scroll', updateActiveSection);
});
</script>

<style scoped>
.legal-content :deep(h1) {
  @apply text-3xl font-bold text-white mt-8 mb-4 first:mt-0;
}

.legal-content :deep(h2) {
  @apply text-2xl font-bold text-white mt-6 mb-3;
}

.legal-content :deep(h3) {
  @apply text-xl font-semibold text-white mt-4 mb-2;
}

.legal-content :deep(p) {
  @apply mb-4 leading-relaxed;
}

.legal-content :deep(ul),
.legal-content :deep(ol) {
  @apply mb-4 ml-6 space-y-2;
}

.legal-content :deep(li) {
  @apply leading-relaxed;
}

.legal-content :deep(strong) {
  @apply font-semibold text-white;
}

.legal-content :deep(a) {
  @apply text-purple-400 hover:text-purple-300 underline;
}

.legal-content :deep(table) {
  @apply w-full mb-4 border-collapse;
}

.legal-content :deep(th),
.legal-content :deep(td) {
  @apply border border-purple-500/20 px-4 py-2;
}

.legal-content :deep(th) {
  @apply bg-purple-500/20 font-semibold;
}

@media (max-width: 1024px) {
  .legal-content {
    @apply text-sm;
  }
}
</style>

