<script setup>
import { computed } from "vue";
import {
  CalendarDays,
  FolderKanban,
  Plus,
  RefreshCw,
} from "lucide-vue-next";

const props = defineProps({
  fromDate: { type: String, default: "" },
  toDate: { type: String, default: "" },
  loading: { type: Boolean, default: false },
  lastUpdated: { type: String, default: "" },
  canCreate: { type: Boolean, default: true },
});

const emit = defineEmits(["date-change", "refresh", "new-project"]);

const today = new Date().toISOString().slice(0, 10);

const yearAgo = (() => {
  const date = new Date();
  date.setFullYear(date.getFullYear() - 1);
  return date.toISOString().slice(0, 10);
})();

const selectedFromDate = computed({
  get: () => props.fromDate || yearAgo,
  set: (value) =>
    emit("date-change", {
      from_date: value,
      to_date: props.toDate || today,
    }),
});

const selectedToDate = computed({
  get: () => props.toDate || today,
  set: (value) =>
    emit("date-change", {
      from_date: props.fromDate || yearAgo,
      to_date: value,
    }),
});

const presets = [
  { label: "30D", days: 30 },
  { label: "90D", days: 90 },
  { label: "6M", days: 182 },
  { label: "1Y", days: 365 },
];

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function applyPreset(days) {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - days);

  emit("date-change", {
    from_date: isoDate(start),
    to_date: isoDate(end),
  });
}

const activePreset = computed(() => {
  const from = props.fromDate || yearAgo;
  const to = props.toDate || today;
  const diff = Math.round(
    (new Date(`${to}T00:00:00`) - new Date(`${from}T00:00:00`)) / 86400000
  );

  const match = presets.find((preset) => Math.abs(diff - preset.days) <= 2);

  return match ? match.days : null;
});
</script>

<template>
  <header class="dashboard-header qb-card">
    <div class="dashboard-header-title">
      <div class="dashboard-header-icon">
        <FolderKanban :size="19" />
      </div>

      <div class="min-w-0">
        <div class="dashboard-header-title-row">
          <h1>Project Management</h1>
          <span class="dashboard-live" :class="{ 'is-loading': loading }">
            <span class="dashboard-live-dot"></span>
            {{ loading ? "Syncing" : "Live" }}
          </span>
        </div>
        <p>
          Projects, tasks, timesheets and project finance
          <span v-if="lastUpdated" class="dashboard-header-updated">
            · Updated {{ lastUpdated }}
          </span>
        </p>
      </div>
    </div>

    <div class="dashboard-header-controls">
      <div class="dashboard-presets" role="group" aria-label="Quick date range">
        <button
          v-for="preset in presets"
          :key="preset.days"
          type="button"
          class="dashboard-preset"
          :class="{ 'is-active': activePreset === preset.days }"
          @click="applyPreset(preset.days)"
        >
          {{ preset.label }}
        </button>
      </div>

      <label class="dashboard-control">
        <span class="dashboard-control-icon"><CalendarDays :size="14" /></span>
        <input
          v-model="selectedFromDate"
          type="date"
          aria-label="From date"
          :max="selectedToDate"
        />
      </label>

      <label class="dashboard-control">
        <span class="dashboard-control-icon"><CalendarDays :size="14" /></span>
        <input
          v-model="selectedToDate"
          type="date"
          aria-label="To date"
          :min="selectedFromDate"
          :max="today"
        />
      </label>

      <button
        type="button"
        class="dashboard-button dashboard-button--secondary"
        :disabled="loading"
        @click="emit('refresh')"
      >
        <RefreshCw :size="14" :class="{ 'dashboard-spin': loading }" />
        {{ loading ? "Loading" : "Refresh" }}
      </button>

      <button
        v-if="canCreate"
        type="button"
        class="dashboard-button"
        @click="emit('new-project')"
      >
        <Plus :size="14" />
        New Project
      </button>
    </div>
  </header>
</template>

<style scoped>
.dashboard-header {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 16px;
  overflow: hidden;
  background:
    radial-gradient(900px 220px at 100% -40%, rgb(196 63 157 / 14%), transparent 60%),
    radial-gradient(720px 220px at 0% -60%, rgb(73 59 145 / 16%), transparent 62%),
    var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 14px;
  box-shadow: 0 8px 24px rgb(31 41 55 / 6%);
}

.dashboard-header::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  content: "";
  background: linear-gradient(180deg, #493b91, #c43f9d);
}

.dashboard-header-title-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.dashboard-live {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  color: #047857;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  background: #ecfdf5;
  border-radius: 999px;
}

.dashboard-live.is-loading {
  color: #b45309;
  background: #fffbeb;
}

.dashboard-live-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgb(16 185 129 / 15%);
  animation: dashboard-pulse 1.8s ease-in-out infinite;
}

@keyframes dashboard-pulse {
  50% {
    opacity: 0.35;
    transform: scale(0.8);
  }
}

.dashboard-presets {
  display: inline-flex;
  flex-shrink: 0;
  height: 34px;
  padding: 2px 3px;
  background: var(--subtle-fg, #f1f4fb);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 8px;
}

.dashboard-preset {
  height: 28px;
  padding: 0 8px;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  font-weight: 650;
  background: transparent;
  border: 0;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.dashboard-preset:hover {
  color: #493b91;
}

.dashboard-preset.is-active {
  color: #ffffff;
  background: linear-gradient(90deg, #493b91, #c43f9d);
  box-shadow: 0 2px 6px rgb(73 59 145 / 25%);
}

.dashboard-header-title {
  display: flex;
  flex: 1 1 0;
  min-width: 150px;
  align-items: center;
  gap: 11px;
}

.dashboard-header-icon {
  display: grid;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  color: #ffffff;
  background: linear-gradient(135deg, #493b91, #c43f9d);
  border-radius: 10px;
  place-items: center;
  box-shadow: 0 4px 10px rgb(73 59 145 / 22%);
}

.dashboard-header-title h1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-header-title p {
  margin: 3px 0 0;
  overflow: hidden;
  color: var(--text-muted, #78809b);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-header-updated {
  white-space: nowrap;
}

.dashboard-header-controls {
  display: flex;
  flex: 0 0 auto;
  flex-wrap: nowrap;
  min-width: 0;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  margin-left: auto;
  white-space: nowrap;
}

.dashboard-header-controls .dashboard-button {
  gap: 6px;
  padding: 0 9px;
}

.dashboard-control {
  display: inline-flex;
  flex-shrink: 0;
  height: 34px;
  min-width: 0;
  align-items: center;
  gap: 6px;
  padding: 0 8px;
  margin: 0;
  line-height: 1;
  vertical-align: middle;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 7px;
}

.dashboard-control-icon {
  display: inline-flex;
  flex-shrink: 0;
  color: #6040c5;
}

.dashboard-control input {
  min-width: 0;
  height: 100%;
  width: 100px;
  padding: 0;
  color: var(--text-color, #333333);
  font-size: 12px;
  font-weight: 500;
  background: transparent;
  border: 0;
  outline: none;
  color-scheme: light;
}

.dashboard-control input::-webkit-calendar-picker-indicator {
  margin: 0;
  padding: 0;
  cursor: pointer;
  opacity: 0.7;
}

.dashboard-spin {
  animation: dashboard-spin 0.9s linear infinite;
}

@keyframes dashboard-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1080px) {
  .dashboard-header-title {
    min-width: 100%;
  }

  .dashboard-header-controls {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    width: 100%;
    margin-left: 0;
    white-space: normal;
  }

  .dashboard-presets {
    grid-column: span 2;
    width: 100%;
  }

  .dashboard-control {
    width: 100%;
  }

  .dashboard-control input {
    width: 100%;
  }

  .dashboard-button {
    grid-column: span 2;
    width: 100%;
  }
}

@media (max-width: 760px) {
  .dashboard-header-controls {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-button {
    grid-column: span 1;
  }

  .dashboard-preset {
    flex: 1;
  }
}

@media (max-width: 600px) {
  .dashboard-header {
    padding: 12px;
  }

  .dashboard-header-title h1 {
    font-size: 17px;
  }
}
</style>
