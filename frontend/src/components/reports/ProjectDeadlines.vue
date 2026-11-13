<script setup>
import { computed, ref } from "vue";
import {
  FolderKanban,
  Milestone,
  Search,
  Timer,
} from "lucide-vue-next";
import { formatDate } from "../../utils/formatters.js";

const props = defineProps({
  records: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["open-record"]);

const searchText = ref("");
const selectedFilter = ref("all");

const DAY_MS = 24 * 60 * 60 * 1000;

function parseDate(value) {
  if (!value) return null;

  const date = new Date(`${value}`.slice(0, 10) + "T00:00:00");

  return Number.isNaN(date.getTime()) ? null : date;
}

function getDaysRemaining(record) {
  const due = parseDate(record.due_date);

  if (!due) return null;

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return Math.round((due.getTime() - today.getTime()) / DAY_MS);
}

function isOverdue(record) {
  const days = getDaysRemaining(record);
  return days !== null && days < 0;
}

function isUpcoming(record) {
  const days = getDaysRemaining(record);
  return days !== null && days >= 0 && days <= 30;
}

function isDueLater(record) {
  const days = getDaysRemaining(record);
  return days !== null && days > 30;
}

const overdueCount = computed(
  () => props.records.filter(isOverdue).length,
);

const upcomingCount = computed(
  () => props.records.filter(isUpcoming).length,
);

const filteredRecords = computed(() => {
  const search = searchText.value.trim().toLowerCase();

  return props.records
    .filter((record) => {
      const title = String(record.title || record.name || "").toLowerCase();
      const id = String(record.name || "").toLowerCase();
      const project = String(record.project || "").toLowerCase();

      const matchesSearch =
        !search ||
        title.includes(search) ||
        id.includes(search) ||
        project.includes(search);

      if (!matchesSearch) return false;

      switch (selectedFilter.value) {
        case "overdue":
          return isOverdue(record);

        case "upcoming":
          return isUpcoming(record);

        case "later":
          return isDueLater(record);

        case "milestone":
          return record.doctype === "Task";

        default:
          return true;
      }
    })
    .sort((a, b) => {
      const aDays = getDaysRemaining(a);
      const bDays = getDaysRemaining(b);

      if (aDays === null) return 1;
      if (bDays === null) return -1;

      return aDays - bDays;
    });
});

function getDeadlineClass(record) {
  const days = getDaysRemaining(record);

  if (days === null) return "deadline-unknown";
  if (days < 0) return "deadline-overdue";
  if (days <= 30) return "deadline-upcoming";

  return "deadline-safe";
}

function getDeadlineLabel(record) {
  const days = getDaysRemaining(record);

  if (days === null) return "No Date";
  if (days < 0) return "Overdue";
  if (days === 0) return "Due Today";
  if (days <= 7) return "Critical";
  if (days <= 30) return "Upcoming";

  return "On Track";
}

function getDeadlineLabelText(record) {
  const days = getDaysRemaining(record);

  if (days === null) return "Due date not set";
  if (days < 0) {
    const overdueDays = Math.abs(days);
    return `${overdueDays} day${overdueDays === 1 ? "" : "s"} overdue`;
  }

  if (days === 0) return "Due today";

  return `In ${days} day${days === 1 ? "" : "s"}`;
}
</script>

<template>
  <section class="table-card qb-card">
    <header class="table-card-header">
      <div class="min-w-0">
        <h2>Project Deadlines</h2>
        <p>Project end dates and milestone tasks</p>
      </div>

      <div class="summary-badges">
        <span class="summary-badge overdue-badge">
          {{ overdueCount }} Overdue
        </span>

        <span class="summary-badge upcoming-badge">
          {{ upcomingCount }} Upcoming
        </span>
      </div>
    </header>

    <div class="table-toolbar">
      <label class="table-search">
        <Search :size="13" />
        <input
          v-model="searchText"
          type="search"
          placeholder="Search projects and tasks..."
          aria-label="Search deadlines"
        />
      </label>

      <select v-model="selectedFilter" class="table-filter">
        <option value="all">All Deadlines</option>
        <option value="overdue">Overdue</option>
        <option value="upcoming">Upcoming (30 days)</option>
        <option value="later">Due Later</option>
        <option value="milestone">Milestones</option>
      </select>
    </div>

    <div v-if="loading" class="table-skeleton">
      <div
        v-for="index in 4"
        :key="index"
        class="skeleton-block table-skeleton-row"
      ></div>
    </div>

    <div v-else-if="filteredRecords.length === 0" class="empty-state">
      No matching deadlines.
    </div>

    <div v-else class="deadline-list">
      <article
        v-for="record in filteredRecords"
        :key="`${record.doctype}-${record.name}`"
        class="deadline-item"
        :class="getDeadlineClass(record)"
        @click="$emit('open-record', record)"
      >
        <span class="deadline-icon">
          <Milestone v-if="record.doctype === 'Task'" :size="14" />
          <FolderKanban v-else :size="14" />
        </span>

        <div class="record-details">
          <div class="record-title-row">
            <h4>{{ record.title || record.name }}</h4>

            <span
              class="deadline-badge"
              :class="getDeadlineClass(record)"
            >
              {{ getDeadlineLabel(record) }}
            </span>
          </div>

          <div class="record-meta">
            <span>
              {{ record.doctype === "Task" ? "Milestone Task" : "Project" }}
            </span>

            <span class="meta-separator">•</span>

            <span>{{ record.name }}</span>

            <template v-if="record.project">
              <span class="meta-separator">•</span>

              <span>{{ record.project }}</span>
            </template>
          </div>

          <div v-if="record.progress !== undefined" class="progress-track">
            <div
              class="progress-fill"
              :class="getDeadlineClass(record)"
              :style="{ width: `${record.progress || 0}%` }"
            ></div>
          </div>
        </div>

        <div class="deadline-info">
          <span class="deadline-label">
            <Timer :size="11" />
            {{ getDeadlineLabelText(record) }}
          </span>

          <strong>{{ formatDate(record.due_date) }}</strong>
        </div>
      </article>
    </div>

    <div v-if="!loading && filteredRecords.length" class="table-footer">
      Showing {{ filteredRecords.length }} of {{ records.length }} deadlines
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
  padding: 4px 9px;
  font-size: 11px;
  font-weight: 650;
  white-space: nowrap;
  border-radius: 999px;
}

.overdue-badge {
  color: #be123c;
  background: #fff1f2;
}

.upcoming-badge {
  color: #b45309;
  background: #fffbeb;
}

.table-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 9px 13px;
}

.table-search {
  display: inline-flex;
  flex: 1 1 160px;
  height: 32px;
  align-items: center;
  gap: 7px;
  padding: 0 10px;
  color: var(--text-muted, #78809b);
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 7px;
}

.table-search input {
  min-width: 0;
  flex: 1;
  height: 100%;
  padding: 0;
  color: var(--text-color, #333333);
  font-size: 12px;
  background: transparent;
  border: 0;
  outline: none;
}

.table-search:focus-within {
  border-color: #c4b8ef;
  box-shadow: 0 0 0 3px rgb(96 64 197 / 8%);
}

.table-filter {
  height: 32px;
  min-width: 150px;
  padding: 0 8px;
  color: var(--text-color, #333333);
  font-size: 12px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 7px;
  outline: none;
}

.deadline-list {
  display: flex;
  flex-direction: column;
  max-height: 264px;
  overflow-y: auto;
  padding: 0 15px;
}

.deadline-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 4px;
  border-top: 1px solid var(--border-color, #f0f2f8);
  cursor: pointer;
}

.deadline-item:first-child {
  border-top: 0;
}

.deadline-item:hover {
  background: var(--subtle-fg, #fafbff);
}

.deadline-icon {
  display: grid;
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  color: #6d28d9;
  font-size: 14px;
  background: #f3eefe;
  border-radius: 8px;
  place-items: center;
}

.deadline-item.deadline-overdue .deadline-icon {
  color: #be123c;
  background: #fff1f2;
}

.deadline-item.deadline-upcoming .deadline-icon {
  color: #b45309;
  background: #fffbeb;
}

.record-details {
  flex: 1;
  min-width: 0;
}

.record-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.record-title-row h4 {
  margin: 0;
  overflow: hidden;
  color: var(--text-color, #17153c);
  font-size: 12px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.deadline-badge {
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 650;
  white-space: nowrap;
  border-radius: 999px;
}

.deadline-badge.deadline-overdue {
  color: #be123c;
  background: #fff1f2;
}

.deadline-badge.deadline-upcoming {
  color: #b45309;
  background: #fffbeb;
}

.deadline-badge.deadline-safe {
  color: #047857;
  background: #ecfdf5;
}

.deadline-badge.deadline-unknown {
  color: #475569;
  background: #f1f5f9;
}

.record-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
}

.meta-separator {
  color: #cbd5e1;
}

.progress-track {
  width: 100%;
  max-width: 260px;
  height: 4px;
  overflow: hidden;
  margin-top: 8px;
  background: #eef1f8;
  border-radius: 6px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #493b91, #c43f9d);
  border-radius: inherit;
  transition: width 0.3s ease;
}

.progress-fill.deadline-overdue {
  background: #e5484d;
}

.progress-fill.deadline-upcoming {
  background: #ffad19;
}

.progress-fill.deadline-unknown {
  background: #78809b;
}

.deadline-info {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  align-items: flex-end;
  gap: 3px;
  min-width: 115px;
}

.deadline-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
}

.deadline-info strong {
  color: var(--text-color, #17153c);
  font-size: 12px;
  font-weight: 650;
  white-space: nowrap;
}

.deadline-item.deadline-overdue .deadline-info strong {
  color: #be123c;
}

.deadline-item.deadline-upcoming .deadline-info strong {
  color: #b45309;
}

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 9px;
  padding: 14px 15px;
}

.table-skeleton-row {
  width: 100%;
  height: 55px;
}

.table-footer {
  padding: 9px 13px;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  border-top: 1px solid var(--border-color, #edf0f7);
}

@media (max-width: 700px) {
  .deadline-item {
    flex-wrap: wrap;
  }

  .record-details {
    min-width: calc(100% - 44px);
  }

  .deadline-info {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding-left: 44px;
  }
}
</style>
