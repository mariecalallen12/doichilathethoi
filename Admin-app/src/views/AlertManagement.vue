<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-white">Alert Management</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Alert Rules Manager -->
      <div class="lg:col-span-2">
        <AlertRulesManager />
      </div>

      <!-- Alert History -->
      <div class="lg:col-span-2">
        <AlertHistory @view-details="openAlertDetails" />
      </div>
    </div>

    <!-- Alert Details Modal -->
    <div
      v-if="showAlertDetails && selectedAlert"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="closeAlertDetails"
    >
      <div class="bg-slate-800 rounded-lg border border-purple-500/30 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-white">Alert Details</h3>
          <button
            @click="closeAlertDetails"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div v-if="selectedAlert" class="space-y-4">
          <div>
            <label class="text-sm text-gray-400">Alert ID</label>
            <p class="text-white">{{ selectedAlert.id }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-400">Rule ID</label>
            <p class="text-white">{{ selectedAlert.alert_rule_id }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-400">User ID</label>
            <p class="text-white">{{ selectedAlert.user_id || 'N/A' }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-400">Severity</label>
            <p class="text-white">{{ selectedAlert.severity }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-400">Triggered At</label>
            <p class="text-white">{{ formatDate(selectedAlert.triggered_at) }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-400">Resolved At</label>
            <p class="text-white">{{ selectedAlert.resolved_at ? formatDate(selectedAlert.resolved_at) : 'Not resolved' }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-400">Conditions Met</label>
            <pre class="bg-slate-700 rounded p-3 text-xs text-white overflow-auto">{{ JSON.stringify(selectedAlert.conditions_met, null, 2) }}</pre>
          </div>
          <div v-if="selectedAlert.actions_taken">
            <label class="text-sm text-gray-400">Actions Taken</label>
            <pre class="bg-slate-700 rounded p-3 text-xs text-white overflow-auto">{{ JSON.stringify(selectedAlert.actions_taken, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AlertHistory from '../components/diagnostics/AlertHistory.vue';
import AlertRulesManager from '../components/diagnostics/AlertRulesManager.vue';

const showAlertDetails = ref(false);
const selectedAlert = ref(null);

function openAlertDetails(alert) {
  selectedAlert.value = alert;
  showAlertDetails.value = true;
}

function closeAlertDetails() {
  showAlertDetails.value = false;
  selectedAlert.value = null;
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
}
</script>

