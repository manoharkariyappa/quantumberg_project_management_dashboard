<script setup>
import { computed } from "vue";
import { ArrowUpRight, Clock3, Users } from "lucide-vue-next";
import { formatHours, formatNumber } from "../../utils/formatters.js";

const props = defineProps({
  members: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["open-tasks"]);

const totalOpen = computed(() =>
  props.members.reduce((total, member) => total + (member.open_tasks || 0), 0)
);

const totalHours = computed(() =>
  props.members.reduce((total, member) => total + (member.hours || 0), 0)
);

const maxOpen = computed(() =>
  Math.max(1, ...props.members.map((member) => member.open_tasks || 0))
);

function initials(value) {
  if (!value) return "?";

  return String(value)
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

function openWidth(member) {
  return Math.round(((member.open_tasks || 0) / maxOpen.value) * 100);
}

function avatarTone(index) {
  const tones = ["tone-purple", "tone-blue", "tone-green", "tone-orange"];
  return tones[index % tones.length];
}
</script>

<template>
  <section class="table-card qb-card">
    <header class="table-card-header">
      <div class="min-w-0">
        <h2>Team Workload</h2>
        <p>Open tasks, overdue items and hours logged per member</p>
      </div>

      <div class="summary-badges">
        <span class="summary-badge open-badge">
          <Users :size="12" />
          {{ formatNumber(totalOpen) }} Open
        </span>

        <span class="summary-badge hours-badge">
          <Clock3 :size="12" />
          {{ formatHours(totalHours) }}
        </span>
      </div>
    </header>

    <div v-if="loading" class="table-skeleton">
      <div
        v-for="index in 4"
        :key="index"
        class="skeleton-block table-skeleton-row"
      ></div>
    </div>

    <div v-else-if="!members.length" class="empty-state">
      No team workload data available.
    </div>

    <div v-else class="workload-list">
      <article
        v-for="(member, index) in members"
        :key="member.user"
        class="workload-item"
        @click="$emit('open-tasks', member)"
      >
        <span class="workload-avatar" :class="avatarTone(index)">
          {{ initials(member.full_name || member.user) }}
        </span>

        <div class="workload-main">
          <div class="workload-title-row">
            <h4>{{ member.full_name || member.user }}</h4>
            <span class="workload-projects">
              {{ formatNumber(member.projects) }} projects
            </span>
          </div>

          <div class="workload-bar">
            <div
              class="workload-bar-fill"
              :class="avatarTone(index)"
              :style="{ width: `${openWidth(member)}%` }"
            ></div>
          </div>

          <div class="workload-meta">
            <span class="meta-open">
              {{ formatNumber(member.open_tasks) }} open
            </span>

            <span class="meta-separator">•</span>
            <span>{{ formatNumber(member.completed_tasks) }} done</span>

            <template v-if="member.overdue_tasks">
              <span class="meta-separator">•</span>
              <span class="meta-danger">
                {{ formatNumber(member.overdue_tasks) }} overdue
              </span>
            </template>
          </div>
        </div>

        <div class="workload-hours">
          <strong>{{ formatHours(member.hours) }}</strong>
          <span>logged</span>
        </div>
      </article>
    </div>

    <div v-if="!loading && members.length" class="table-footer">
      <button type="button" class="dashboard-link" @click="$emit('open-tasks')">
        View all tasks
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

.open-badge {
  color: #1d4ed8;
  background: #eff6ff;
}

.hours-badge {
  color: #6d28d9;
  background: #f3eefe;
}

.workload-list {
  display: flex;
  flex-direction: column;
  max-height: 264px;
  overflow-y: auto;
  padding: 0 15px;
}

.workload-item {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 11px 4px;
  border-top: 1px solid var(--border-color, #f0f2f8);
  cursor: pointer;
}

.workload-item:first-child {
  border-top: 0;
}

.workload-item:hover {
  background: var(--subtle-fg, #fafbff);
}

.workload-avatar {
  display: grid;
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  border-radius: 50%;
  place-items: center;
}

.tone-purple {
  background: linear-gradient(135deg, #493b91, #c43f9d);
}

.tone-blue {
  background: linear-gradient(135deg, #2563eb, #3987f5);
}

.tone-green {
  background: linear-gradient(135deg, #059669, #20bf88);
}

.tone-orange {
  background: linear-gradient(135deg, #ea580c, #ffad19);
}

.workload-main {
  flex: 1;
  min-width: 0;
}

.workload-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.workload-title-row h4 {
  margin: 0;
  overflow: hidden;
  max-width: 220px;
  color: var(--text-color, #17153c);
  font-size: 12px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workload-projects {
  color: var(--text-muted, #78809b);
  font-size: 10px;
  white-space: nowrap;
}

.workload-bar {
  width: 100%;
  height: 5px;
  overflow: hidden;
  margin-top: 6px;
  background: #eef1f8;
  border-radius: 6px;
}

.workload-bar-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.3s ease;
}

.workload-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  margin-top: 5px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
}

.meta-open {
  color: #493b91;
  font-weight: 650;
}

.meta-separator {
  color: #cbd5e1;
}

.meta-danger {
  color: #be123c;
  font-weight: 650;
}

.workload-hours {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  align-items: flex-end;
  min-width: 58px;
}

.workload-hours strong {
  color: var(--text-color, #17153c);
  font-size: 13px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.workload-hours span {
  color: var(--text-muted, #78809b);
  font-size: 10px;
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
</style>
