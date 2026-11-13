<script setup>
import { computed } from "vue";
import {
  ArrowUpRight,
  CheckCircle2,
  CircleAlert,
  FolderKanban,
  ShieldAlert,
  ShieldCheck,
} from "lucide-vue-next";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
} from "../../utils/formatters.js";

const props = defineProps({
  projects: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },

  currency: {
    type: String,
    default: "INR",
  },
});

defineEmits(["open-project", "open-all"]);

const atRiskCount = computed(
  () =>
    props.projects.filter((project) =>
      ["At Risk", "Overdue", "Over Budget"].includes(project.health)
    ).length
);

const onTrackCount = computed(
  () => props.projects.filter((project) => project.health === "On Track").length
);

function healthClass(health) {
  const classes = {
    Overdue: "health-overdue",
    "At Risk": "health-risk",
    "Over Budget": "health-over-budget",
    Watch: "health-watch",
    "On Track": "health-ontrack",
    Completed: "health-completed",
    Cancelled: "health-neutral",
  };

  return classes[health] || "health-neutral";
}

function healthIcon(health) {
  if (health === "On Track" || health === "Completed") {
    return health === "Completed" ? CheckCircle2 : ShieldCheck;
  }

  if (health === "At Risk" || health === "Over Budget") {
    return ShieldAlert;
  }

  return CircleAlert;
}

function statusClass(status) {
  const classes = {
    Open: "status-open",
    "On hold": "status-on-hold",
    Completed: "status-completed",
    Cancelled: "status-cancelled",
  };

  return classes[status] || "status-neutral";
}

function utilization(project) {
  return Math.max(0, Math.min(100, Math.round(project.utilization || 0)));
}

function daysLabel(project) {
  if (project.days_remaining === null || project.days_remaining === undefined) {
    return "No due date";
  }

  if (project.days_remaining < 0) {
    return `${Math.abs(project.days_remaining)}d overdue`;
  }

  if (project.days_remaining === 0) {
    return "Due today";
  }

  return `${project.days_remaining}d left`;
}
</script>

<template>
  <section class="table-card qb-card">
    <header class="table-card-header">
      <div class="min-w-0">
        <h2>Project Health</h2>
        <p>Budget burn, schedule and delivery risk</p>
      </div>

      <div class="summary-badges">
        <span class="summary-badge risk-badge">
          <ShieldAlert :size="12" />
          {{ atRiskCount }} At Risk
        </span>

        <span class="summary-badge track-badge">
          <ShieldCheck :size="12" />
          {{ onTrackCount }} On Track
        </span>
      </div>
    </header>

    <div v-if="loading" class="table-skeleton">
      <div
        v-for="index in 5"
        :key="index"
        class="skeleton-block table-skeleton-row"
      ></div>
    </div>

    <div v-else-if="!projects.length" class="empty-state">
      No project health data available.
    </div>

    <div v-else class="health-list">
      <article
        v-for="project in projects"
        :key="project.name"
        class="health-item"
        @click="$emit('open-project', project)"
      >
        <span class="health-icon" :class="healthClass(project.health)">
          <component :is="healthIcon(project.health)" :size="16" />
        </span>

        <div class="health-main">
          <div class="health-title-row">
            <h4>{{ project.project_name || project.name }}</h4>

            <span class="health-badge" :class="healthClass(project.health)">
              {{ project.health }}
            </span>

            <span class="status-pill" :class="statusClass(project.status)">
              <span class="status-pill-dot"></span>
              {{ project.status || "Open" }}
            </span>
          </div>

          <div class="health-meta">
            <span class="health-id">
              <FolderKanban :size="11" />
              {{ project.name }}
            </span>

            <span class="meta-separator">•</span>
            <span>{{ formatNumber(project.open_tasks) }} open tasks</span>

            <template v-if="project.overdue_tasks">
              <span class="meta-separator">•</span>
              <span class="meta-danger">
                {{ formatNumber(project.overdue_tasks) }} overdue
              </span>
            </template>

            <span class="meta-separator">•</span>
            <span>
              {{ formatCurrency(project.actual_cost, currency) }} of
              {{ formatCurrency(project.budget, currency) }}
            </span>
          </div>

          <div class="health-progress">
            <div class="health-progress-track">
              <div
                class="health-progress-fill"
                :class="healthClass(project.health)"
                :style="{ width: `${utilization(project)}%` }"
              ></div>
            </div>

            <span>{{ formatPercent(utilization(project)) }} budget used</span>
          </div>
        </div>

        <div class="health-side">
          <strong :class="healthClass(project.health)">
            {{ formatPercent(project.completion) }}
          </strong>
          <span>complete</span>
          <small>{{ daysLabel(project) }}</small>
        </div>
      </article>
    </div>

    <div v-if="!loading && projects.length" class="table-footer">
      <button type="button" class="dashboard-link" @click="$emit('open-all')">
        View all projects
        <ArrowUpRight :size="13" />
      </button>
    </div>
  </section>
</template>

<style scoped>
.table-card {
  display: flex;
  flex-direction: column;
}

.table-card-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 13px 8px;
  border-bottom: 1px solid var(--border-color, #edf0f7);
}

.table-card-header h2 {
  overflow: hidden;
  color: var(--text-color, #17153c);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-card-header p {
  margin: 3px 0 0;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  line-height: 1.4;
}

.summary-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 9px;
  font-size: 11px;
  font-weight: 650;
  white-space: nowrap;
  border-radius: 999px;
}

.risk-badge {
  color: #be123c;
  background: #fff1f2;
}

.track-badge {
  color: #047857;
  background: #ecfdf5;
}

.health-list {
  display: flex;
  flex-direction: column;
  max-height: 264px;
  overflow-y: auto;
  padding: 0 15px;
}

.health-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 4px;
  border-top: 1px solid var(--border-color, #f0f2f8);
  cursor: pointer;
}

.health-item:first-child {
  border-top: 0;
}

.health-item:hover {
  background: var(--subtle-fg, #fafbff);
}

.health-icon {
  display: grid;
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  place-items: center;
}

.health-main {
  flex: 1;
  min-width: 0;
}

.health-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px;
}

.health-title-row h4 {
  margin: 0;
  overflow: hidden;
  max-width: 240px;
  color: var(--text-color, #17153c);
  font-size: 12px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.health-badge {
  padding: 2px 7px;
  font-size: 10px;
  font-weight: 650;
  white-space: nowrap;
  border-radius: 999px;
}

.health-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  margin-top: 4px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
}

.health-id {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.meta-separator {
  color: #cbd5e1;
}

.meta-danger {
  color: #be123c;
  font-weight: 650;
}

.health-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 7px;
}

.health-progress-track {
  width: 100%;
  max-width: 230px;
  height: 5px;
  overflow: hidden;
  background: #eef1f8;
  border-radius: 6px;
}

.health-progress-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.3s ease;
}

.health-progress span {
  flex-shrink: 0;
  color: var(--text-muted, #78809b);
  font-size: 10px;
  font-variant-numeric: tabular-nums;
}

.health-side {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  align-items: flex-end;
  gap: 1px;
  min-width: 74px;
}

.health-side strong {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.health-side span,
.health-side small {
  color: var(--text-muted, #78809b);
  font-size: 10px;
  white-space: nowrap;
}

.health-side small {
  margin-top: 2px;
  padding: 1px 6px;
  background: var(--subtle-fg, #f8f9fd);
  border-radius: 999px;
}

.health-overdue {
  color: #be123c;
  background: #fff1f2;
}

.health-risk {
  color: #b45309;
  background: #fffbeb;
}

.health-over-budget {
  color: #c2410c;
  background: #fff7ed;
}

.health-watch {
  color: #6d28d9;
  background: #f3eefe;
}

.health-ontrack {
  color: #047857;
  background: #ecfdf5;
}

.health-completed {
  color: #1d4ed8;
  background: #eff6ff;
}

.health-neutral {
  color: #475569;
  background: #f1f5f9;
}

.health-progress-fill.health-overdue {
  background: linear-gradient(90deg, #e5484d, #be123c);
}

.health-progress-fill.health-risk {
  background: linear-gradient(90deg, #ffad19, #f59e0b);
}

.health-progress-fill.health-over-budget {
  background: linear-gradient(90deg, #fb923c, #c2410c);
}

.health-progress-fill.health-watch {
  background: linear-gradient(90deg, #6040c5, #c43f9d);
}

.health-progress-fill.health-ontrack,
.health-progress-fill.health-completed {
  background: linear-gradient(90deg, #20bf88, #0f9f8f);
}

.health-progress-fill.health-neutral {
  background: #94a3b8;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.5;
  white-space: nowrap;
  border-radius: 999px;
}

.status-pill-dot {
  flex-shrink: 0;
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
}

.status-open {
  color: #1d4ed8;
  background: #eff6ff;
}

.status-on-hold {
  color: #b45309;
  background: #fffbeb;
}

.status-completed {
  color: #047857;
  background: #ecfdf5;
}

.status-cancelled {
  color: #be123c;
  background: #fff1f2;
}

.status-neutral {
  color: #475569;
  background: #f1f5f9;
}

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 9px;
  padding: 14px 15px;
}

.table-skeleton-row {
  width: 100%;
  height: 52px;
}

.empty-state {
  padding: 24px;
  color: var(--text-muted, #78809b);
  font-size: 12px;
  text-align: center;
}

.table-footer {
  padding: 9px 13px;
  border-top: 1px solid var(--border-color, #edf0f7);
}

@media (max-width: 700px) {
  .health-item {
    flex-wrap: wrap;
  }

  .health-main {
    min-width: calc(100% - 46px);
  }

  .health-side {
    flex-direction: row;
    align-items: center;
    gap: 6px;
    width: 100%;
    padding-left: 46px;
  }
}
</style>
