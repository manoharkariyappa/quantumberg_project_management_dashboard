<script setup>
import { computed, ref } from "vue";
import { ArrowUpRight, Briefcase, Search } from "lucide-vue-next";
import {
  formatCurrency,
  formatDate,
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

defineEmits(["view-all", "open-project"]);

const search = ref("");
const statusFilter = ref("all");

const filteredProjects = computed(() => {
  const query = search.value.trim().toLowerCase();

  return props.projects.filter((project) => {
    const name = String(
      project.project_name || project.name || "",
    ).toLowerCase();

    const id = String(project.name || "").toLowerCase();

    const manager = String(
      project.project_manager || "",
    ).toLowerCase();

    const matchesSearch =
      !query ||
      name.includes(query) ||
      id.includes(query) ||
      manager.includes(query);

    const matchesStatus =
      statusFilter.value === "all" ||
      project.status === statusFilter.value;

    return matchesSearch && matchesStatus;
  });
});

function progressValue(project) {
  const value = Number(project.percent_complete || 0);

  return Math.max(0, Math.min(100, Math.round(value)));
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
</script>

<template>
  <section class="table-card qb-card">
    <header class="table-card-header">
      <div class="min-w-0">
        <h2>Recent Projects</h2>
        <p>Track project progress and budgets</p>
      </div>

      <button
        type="button"
        class="dashboard-link"
        @click="$emit('view-all')"
      >
        View All
        <ArrowUpRight :size="13" />
      </button>
    </header>

    <div class="table-toolbar">
      <label class="table-search">
        <Search :size="13" />
        <input
          v-model="search"
          type="search"
          placeholder="Search projects..."
          aria-label="Search projects"
        />
      </label>

      <select
        v-model="statusFilter"
        class="table-filter"
        aria-label="Filter projects by status"
      >
        <option value="all">All Statuses</option>
        <option value="Open">Open</option>
        <option value="On hold">On Hold</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
    </div>

    <div v-if="loading" class="table-skeleton">
      <div
        v-for="index in 5"
        :key="index"
        class="skeleton-block table-skeleton-row"
      ></div>
    </div>

    <div v-else-if="filteredProjects.length === 0" class="empty-state">
      No projects found.
    </div>

    <div v-else class="table-scroll">
      <table class="qb-table">
        <thead>
          <tr>
            <th>Project</th>
            <th>Manager</th>
            <th>Status</th>
            <th>Progress</th>
            <th class="numeric">Budget</th>
            <th class="numeric">Actual Cost</th>
            <th>Due Date</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="project in filteredProjects"
            :key="project.name"
            @click="$emit('open-project', project)"
          >
            <td>
              <div class="table-doc-cell">
                <span class="table-doc-icon">
                  <Briefcase :size="13" />
                </span>

                <div class="min-w-0">
                  <button
                    class="table-doc-link"
                    type="button"
                    @click.stop="$emit('open-project', project)"
                  >
                    {{ project.project_name || project.name }}
                  </button>

                  <small class="table-doc-id">{{ project.name }}</small>
                </div>
              </div>
            </td>

            <td>{{ project.project_manager || "—" }}</td>

            <td>
              <span class="status-pill" :class="statusClass(project.status)">
                <span class="status-pill-dot"></span>
                {{ project.status || "Not Set" }}
              </span>
            </td>

            <td>
              <div class="progress-cell">
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :style="{
                      width: `${progressValue(project)}%`,
                    }"
                  ></div>
                </div>

                <span>{{ formatPercent(progressValue(project)) }}</span>
              </div>
            </td>

            <td class="numeric amount-cell">
              {{ formatCurrency(project.budget, currency) }}
            </td>

            <td class="numeric amount-cell">
              {{ formatCurrency(project.actual_cost, currency) }}
            </td>

            <td class="date-cell">
              {{ formatDate(project.expected_end_date) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="!loading && filteredProjects.length"
      class="table-footer"
    >
      Showing {{ filteredProjects.length }} of {{ projects.length }} projects
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

.numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.amount-cell {
  font-weight: 650;
}

.date-cell {
  color: var(--text-muted, #78809b);
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
  max-width: 190px;
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
  max-width: 190px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.progress-cell {
  display: flex;
  align-items: center;
  gap: 7px;
}

.progress-track {
  width: 64px;
  height: 6px;
  overflow: hidden;
  background: #eef1f8;
  border-radius: 6px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #493b91, #c43f9d);
  border-radius: inherit;
  transition: width 0.3s ease;
}

.progress-cell > span {
  min-width: 30px;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  font-variant-numeric: tabular-nums;
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
