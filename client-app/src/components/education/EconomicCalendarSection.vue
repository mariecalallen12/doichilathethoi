<template>
  <section id="calendar" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Lịch Kinh Tế</h2>
      <p class="text-purple-200/80">Sự kiện quan trọng real-time</p>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex flex-col md:flex-row gap-4">
      <select
        v-model="selectedCountry"
        @change="handleFilterChange"
        class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
      >
        <option value="all">Tất cả quốc gia</option>
        <option value="US">Hoa Kỳ</option>
        <option value="EU">Châu Âu</option>
        <option value="UK">Anh</option>
        <option value="JP">Nhật Bản</option>
        <option value="CN">Trung Quốc</option>
        <option value="AU">Úc</option>
      </select>
      <select
        v-model="selectedImportance"
        @change="handleFilterChange"
        class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
      >
        <option value="all">Tất cả mức độ</option>
        <option value="high">Cao</option>
        <option value="medium">Trung bình</option>
        <option value="low">Thấp</option>
      </select>
      <input
        v-model="dateRange.start"
        type="date"
        class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
        @change="handleFilterChange"
      />
      <input
        v-model="dateRange.end"
        type="date"
        class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
        @change="handleFilterChange"
      />
    </div>

    <!-- Loading State -->
    <div v-if="educationStore.isLoading" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
      <div class="flex items-center justify-center h-96">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400 mb-4"></div>
          <p class="text-purple-200">Đang tải lịch kinh tế...</p>
        </div>
      </div>
    </div>

    <!-- Calendar -->
    <div v-else class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
      <FullCalendar :options="calendarOptions" class="calendar-container" />
    </div>

    <!-- Empty State -->
    <div v-if="!educationStore.isLoading && filteredEvents.length === 0" class="text-center py-12">
      <div class="max-w-md mx-auto">
        <i class="fas fa-calendar-times text-6xl text-purple-400/50 mb-4"></i>
        <h3 class="text-xl font-bold text-white mb-2">Không có sự kiện</h3>
        <p class="text-gray-400 mb-4">Không có sự kiện kinh tế nào trong khoảng thời gian đã chọn</p>
        <button
          @click="resetFilters"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all"
        >
          Đặt lại bộ lọc
        </button>
      </div>
    </div>

    <!-- Event List -->
    <div class="mt-6 space-y-4">
      <div
        v-for="event in filteredEvents"
        :key="event.id"
        class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-lg p-4 border border-purple-500/20 hover:border-purple-400/40 transition-all cursor-pointer"
        @click="openEventDetail(event)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <span
                class="px-2 py-1 rounded text-xs font-semibold"
                :class="{
                  'bg-red-500/20 text-red-400': event.importance === 'high',
                  'bg-yellow-500/20 text-yellow-400': event.importance === 'medium',
                  'bg-green-500/20 text-green-400': event.importance === 'low'
                }"
              >
                {{ getImportanceLabel(event.importance) }}
              </span>
              <span class="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
                {{ event.country }}
              </span>
              <span class="text-gray-400 text-sm">
                {{ formatDate(event.date) }}
              </span>
            </div>
            <h3 class="text-white font-bold mb-1">{{ event.title }}</h3>
            <p class="text-gray-400 text-sm">{{ event.description }}</p>
          </div>
          <div class="ml-4">
            <i class="fas fa-chevron-right text-purple-400"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Detail Modal -->
    <EventDetailModal
      v-if="selectedEvent"
      :event="selectedEvent"
      @close="closeEventDetail"
    />
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useEducationStore } from '../../stores/education';
import EventDetailModal from './EventDetailModal.vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';

const educationStore = useEducationStore();
const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay'
  },
  height: 'auto',
  contentHeight: 600,
  eventDisplay: 'block',
  dayMaxEvents: 3,
  moreLinkClick: 'popover',
  eventClick: (info) => {
    const eventData = educationStore.calendar.find(e => e.id.toString() === info.event.id);
    if (eventData) {
      openEventDetail(eventData);
    }
  }
});
const selectedCountry = ref('all');
const selectedImportance = ref('all');
const dateRange = ref({
  start: new Date().toISOString().split('T')[0],
  end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
});
const selectedEvent = ref(null);

const filteredEvents = computed(() => {
  let events = educationStore.calendar;

  if (selectedCountry.value !== 'all') {
    events = events.filter(e => e.country === selectedCountry.value);
  }

  if (selectedImportance.value !== 'all') {
    events = events.filter(e => e.importance === selectedImportance.value);
  }

  if (dateRange.value.start) {
    events = events.filter(e => new Date(e.date) >= new Date(dateRange.value.start));
  }

  if (dateRange.value.end) {
    events = events.filter(e => new Date(e.date) <= new Date(dateRange.value.end));
  }

  return events.sort((a, b) => new Date(a.date) - new Date(b.date));
});

const handleFilterChange = () => {
  // Refetch calendar with filters
  educationStore.fetchCalendar(dateRange.value.start, dateRange.value.end);
};

const resetFilters = () => {
  selectedCountry.value = 'all';
  selectedImportance.value = 'all';
  const now = new Date();
  dateRange.value = {
    start: new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0],
    end: new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0]
  };
  handleFilterChange();
};

const openEventDetail = (event) => {
  selectedEvent.value = event;
};

const closeEventDetail = () => {
  selectedEvent.value = null;
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getImportanceLabel = (importance) => {
  const labels = {
    high: 'Cao',
    medium: 'Trung bình',
    low: 'Thấp'
  };
  return labels[importance] || importance;
};

const getImportanceColor = (importance) => {
  const colors = {
    high: '#ef4444',
    medium: '#eab308',
    low: '#22c55e'
  };
  return colors[importance] || '#6b7280';
};

// Update calendar events when filtered events change
watch([filteredEvents, () => educationStore.calendar], () => {
  calendarOptions.value.events = filteredEvents.value.map(event => ({
    id: event.id.toString(),
    title: event.title,
    start: event.date,
    backgroundColor: getImportanceColor(event.importance),
    borderColor: getImportanceColor(event.importance),
    textColor: '#ffffff',
    extendedProps: {
      importance: event.importance,
      country: event.country,
      description: event.description,
      actual: event.actual,
      forecast: event.forecast,
      previous: event.previous
    }
  }));
}, { immediate: true });

onMounted(() => {
  // Fetch calendar for current month
  const now = new Date();
  const startDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
  const endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString();
  educationStore.fetchCalendar(startDate, endDate);
});
</script>

<style scoped>
.calendar-container {
  min-height: 400px;
}

/* FullCalendar custom styles */
:deep(.fc) {
  color: #e2e8f0;
}

:deep(.fc-header-toolbar) {
  margin-bottom: 1.5rem;
}

:deep(.fc-button) {
  background-color: #7c3aed;
  border-color: #7c3aed;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

:deep(.fc-button:hover) {
  background-color: #6d28d9;
  border-color: #6d28d9;
}

:deep(.fc-button-active) {
  background-color: #5b21b6;
  border-color: #5b21b6;
}

:deep(.fc-today-button) {
  background-color: #8b5cf6;
  border-color: #8b5cf6;
}

:deep(.fc-daygrid-day) {
  background-color: rgba(30, 41, 59, 0.5);
}

:deep(.fc-day-today) {
  background-color: rgba(139, 92, 246, 0.2) !important;
}

:deep(.fc-daygrid-day-number) {
  color: #e2e8f0;
  padding: 0.5rem;
}

:deep(.fc-col-header-cell) {
  background-color: rgba(51, 65, 85, 0.5);
  color: #cbd5e1;
  padding: 0.75rem;
}

:deep(.fc-event) {
  border-radius: 0.375rem;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

:deep(.fc-event:hover) {
  opacity: 0.8;
  transform: scale(1.02);
}

:deep(.fc-event-title) {
  font-weight: 500;
  padding: 0.125rem;
}

:deep(.fc-popover) {
  background-color: #1e293b;
  border-color: #7c3aed;
}

:deep(.fc-popover-header) {
  background-color: #334155;
  color: #e2e8f0;
}

:deep(.fc-popover-body) {
  background-color: #1e293b;
}

@media (max-width: 768px) {
  :deep(.fc-header-toolbar) {
    flex-direction: column;
    gap: 0.5rem;
  }

  :deep(.fc-toolbar-chunk) {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
  }

  :deep(.fc-button) {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
  }
}
</style>

