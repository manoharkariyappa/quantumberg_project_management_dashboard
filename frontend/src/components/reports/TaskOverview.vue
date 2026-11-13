<script setup>
import { computed, ref } from "vue";
import { ClipboardList, Search } from "lucide-vue-next";
import { formatDate } from "../../utils/formatters.js";

const props = defineProps({
  tasks: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["open-task"]);

const search = ref("");
const statusFilter = ref("all");

const filteredTasks = computed(() => {
  const query = search.value.trim().toLowerCase();

  return props.tasks.filter((task) => {
    const subject = String(
      task.subject || task.name || "",
    ).toLowerCase();

    const project = String(
      task.project || "",
    ).toLowerCase();

    const assignedTo = String(
      task.assigned_to || task.owner || "",
    ).toLowerCase();

    const matchesSearch =
      !query ||
      subject.includes(query) ||
      project.includes(query) ||
      assignedTo.includes(query);

    const matchesStatus =
      statusFilter.value === "all" ||
      task.status === statusFilter.value;

    return matchesSearch && matchesStatus;
  });
});

function initials(value) {
  if (!value) return "?";

  return String(value)
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

function statusClass(status) {
  const classes = {
    Open: "status-open",
    Working: "status-working",
    "Pending Review": "status-review",
    Overdue: "status-overdue",
    Completed: "status-completed",
    Cancelled: "status-cancelled",
  };

  return classes[status] || "status-neutral";
}

function priorityClass(priority) {
  const classes = {
    Urgent: "priority-urgent",
    High: "priority-high",
    Medium: "priority-medium",
    Low: "priority-low",
  };

  return classes[priority] || "priority-medium";
}
</script>

<template>
  <section class="table-card qb-card">
    <header class="table-card-header">
      <div class="min-w-0">
        <h2>Task Overview</h2>
        <p>Monitor project tasks and deadlines</p>
      </div>

      <span class="task-count">
        {{ filteredTasks.length }} Tasks
      </span>
    </header>

    <div class="table-toolbar">
      <label class="table-search">
        <Search :size="13" />
        <input
          v-model="search"
          type="search"
          placeholder="Search tasks..."
          aria-label="Search tasks"
        />
      </label>

      <select
        v-model="statusFilter"
        class="table-filter"
        aria-label="Filter tasks by status"
      >
        <option value="all">All Statuses</option>
        <option value="Open">Open</option>
        <option value="Working">Working</option>
        <option value="Pending Review">Pending Review</option>
        <option value="Overdue">Overdue</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
    </div>

    <div v-if="loading" class="table-skeleton">
      <div
        v-for="index in 6"
        :key="index"
        class="skeleton-block table-skeleton-row"
      ></div>
    </div>

    <div v-else-if="!filteredTasks.length" class="empty-state">
      No tasks found.
    </div>

    <div v-else class="table-scroll">
      <table class="qb-table">
        <thead>
          <tr>
            <th>Task</th>
            <th>Project</th>
            <th>Assigned To</th>
            <th>Priority</th>
            <th>Due Date</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="task in filteredTasks"
            :key="task.name"
            @click="$emit('open-task', task)"
          >
            <td>
              <div class="table-doc-cell">
                <span class="table-doc-icon">
                  <ClipboardList :size="13" />
                </span>

                <div class="min-w-0">
                  <button
                    class="table-doc-link"
                    type="button"
                    @click.stop="$emit('open-task', task)"
                  >
                    {{ task.subject || task.name }}
                  </button>

                  <small class="table-doc-id">
                    {{ task.name }}{{ task.is_milestone ? " · Milestone" : "" }}
                  </small>
                </div>
              </div>
            </td>

            <td class="project-cell">
              {{ task.project || "—" }}
            </td>

            <td>
              <div class="assignee-cell">
                <span class="assignee-avatar">
                  {{ initials(task.assigned_to || task.owner) }}
                </span>

                <span class="assignee-name">
                  {{ task.assigned_to || task.owner || "Unassigned" }}
                </span>
              </div>
            </td>

            <td>
              <span class="priority-pill" :class="priorityClass(task.priority)">
                {{ task.priority || "Medium" }}
              </span>
            </td>

            <td>
              <span
                class="date-cell"
                :class="{ 'date-overdue': task.is_overdue }"
              >
                {{ formatDate(task.exp_end_date || task.due_date) }}
              </span>
            </td>

            <td>
              <span class="status-pill" :class="statusClass(task.status)">
                <span class="status-pill-dot"></span>
                {{ task.status || "Open" }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="!loading && filteredTasks.length"
      class="table-footer"
    >
      Showing {{ filteredTasks.length }} of {{ tasks.length }} tasks
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

.task-count {
  flex-shrink: 0;
  padding: 4px 9px;
  color: #6d28d9;
  font-size: 11px;
  font-weight: 650;
  background: #f3eefe;
  border-radius: 999px;
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
  min-width: 130px;
  padding: 0 8px;
  color: var(--text-color, #333333);
  font-size: 12px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 7px;
  outline: none;
}

.table-scroll {
  width: 100%;
  max-height: 264px;
  overflow: auto;
}

.qb-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}

.qb-table th {
  padding: 9px 12px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.25px;
  text-align: left;
  text-transform: uppercase;
  white-space: nowrap;
  background: var(--subtle-fg, #f8f9fd);
  border-bottom: 1px solid var(--border-color, #edf0f7);
}

.qb-table td {
  padding: 9px 12px;
  color: var(--text-color, #333333);
  font-size: 12px;
  vertical-align: middle;
  border-bottom: 1px solid var(--border-color, #f0f2f8);
}

.qb-table tbody tr {
  cursor: pointer;
}

.qb-table tbody tr:last-child td {
  border-bottom: 0;
}

.qb-table tbody tr:hover {
  background: var(--subtle-fg, #fafbff);
}

.table-doc-cell {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
}

.table-doc-icon {
  display: grid;
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  color: #6d28d9;
  font-size: 13px;
  background: #f3eefe;
  border-radius: 8px;
  place-items: center;
}

.table-doc-link {
  padding: 0;
  overflow: hidden;
  max-width: 210px;
  color: #6040c5;
  font-size: 12px;
  font-weight: 600;
  background: transparent;
  border: 0;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.table-doc-link:hover {
  color: #493b91;
  text-decoration: underline;
}

.table-doc-id {
  display: block;
  overflow: hidden;
  max-width: 210px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-cell {
  color: var(--text-muted, #78809b);
}

.assignee-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.assignee-avatar {
  display: grid;
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  background: linear-gradient(135deg, #493b91, #c43f9d);
  border-radius: 50%;
  place-items: center;
}

.assignee-name {
  overflow: hidden;
  max-width: 130px;
  color: var(--text-color, #333333);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.priority-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.5;
  white-space: nowrap;
  border-radius: 999px;
}

.priority-urgent {
  color: #be123c;
  background: #fff1f2;
}

.priority-high {
  color: #b45309;
  background: #fffbeb;
}

.priority-medium {
  color: #1d4ed8;
  background: #eff6ff;
}

.priority-low {
  color: #475569;
  background: #f1f5f9;
}

.date-cell {
  color: var(--text-muted, #78809b);
  white-space: nowrap;
}

.date-overdue {
  color: #be123c;
  font-weight: 650;
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

.status-working {
  color: #6d28d9;
  background: #f3eefe;
}

.status-review {
  color: #b45309;
  background: #fffbeb;
}

.status-overdue {
  color: #be123c;
  background: #fff1f2;
}

.status-completed {
  color: #047857;
  background: #ecfdf5;
}

.status-cancelled {
  color: #475569;
  background: #f1f5f9;
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
  height: 33px;
}

.table-footer {
  padding: 9px 13px;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  border-top: 1px solid var(--border-color, #edf0f7);
}
</style>
