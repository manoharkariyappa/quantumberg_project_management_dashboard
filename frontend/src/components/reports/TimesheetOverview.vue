<script setup>
import { computed, ref } from "vue";
import { Clock, Search, Timer } from "lucide-vue-next";
import {
  formatCurrency,
  formatHours,
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

defineEmits(["open-project"]);

const searchText = ref("");
const selectedFilter = ref("all");

const totalHours = computed(() =>
  props.projects.reduce(
    (sum, row) => sum + Number(row.total_hours || 0),
    0,
  ),
);

const totalBilling = computed(() =>
  props.projects.reduce(
    (sum, row) => sum + Number(row.billing_amount || 0),
    0,
  ),
);

const filteredProjects = computed(() => {
  const search = searchText.value.trim().toLowerCase();

  return props.projects.filter((row) => {
    const project = String(
      row.project_name || row.project || "",
    ).toLowerCase();

    const matchesSearch = !search || project.includes(search);

    if (!matchesSearch) {
      return false;
    }

    switch (selectedFilter.value) {
      case "open":
        return row.status === "Open";

      case "completed":
        return row.status === "Completed";

      default:
        return true;
    }
  });
});

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
        <h2>Timesheet Overview</h2>
        <p>Hours logged and billed per project</p>
      </div>

      <div class="summary-badges">
        <span class="summary-badge hours-badge">
          <Timer :size="12" />
          {{ formatHours(totalHours) }} Logged
        </span>

        <span class="summary-badge billed-badge">
          {{ formatCurrency(totalBilling, currency) }} Billed
        </span>
      </div>
    </header>

    <div class="table-toolbar">
      <label class="table-search">
        <Search :size="13" />
        <input
          v-model="searchText"
          type="search"
          placeholder="Search project..."
          aria-label="Search timesheet projects"
        />
      </label>

      <select v-model="selectedFilter" class="table-filter">
        <option value="all">All Projects</option>
        <option value="open">Open Projects</option>
        <option value="completed">Completed Projects</option>
      </select>
    </div>

    <div v-if="loading" class="table-skeleton">
      <div
        v-for="index in 4"
        :key="index"
        class="skeleton-block table-skeleton-row"
      ></div>
    </div>

    <div v-else-if="filteredProjects.length === 0" class="empty-state">
      No timesheet hours logged for this period.
    </div>

    <div v-else class="table-scroll">
      <table class="qb-table">
        <thead>
          <tr>
            <th>Project</th>
            <th>Status</th>
            <th class="numeric">Hours</th>
            <th class="numeric">Billable</th>
            <th class="numeric">Billing Amount</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="row in filteredProjects"
            :key="row.project"
            @click="$emit('open-project', row)"
          >
            <td>
              <div class="table-doc-cell">
                <span class="table-doc-icon">
                  <Clock :size="13" />
                </span>

                <div class="min-w-0">
                  <span class="table-doc-link">
                    {{ row.project_name || row.project }}
                  </span>

                  <small class="table-doc-id">{{ row.project }}</small>
                </div>
              </div>
            </td>

            <td>
              <span class="status-pill" :class="statusClass(row.status)">
                <span class="status-pill-dot"></span>
                {{ row.status || "Open" }}
              </span>
            </td>

            <td class="numeric hours-cell">
              {{ formatHours(row.total_hours) }}
            </td>

            <td class="numeric billable-cell">
              {{ formatHours(row.billable_hours) }}
            </td>

            <td class="numeric amount-cell">
              {{ formatCurrency(row.billing_amount, currency) }}
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
  gap: 6px;
  padding: 4px 9px;
  font-size: 11px;
  font-weight: 650;
  white-space: nowrap;
  border-radius: 999px;
}

.hours-badge {
  color: #1d4ed8;
  background: #eff6ff;
}

.billed-badge {
  color: #6d28d9;
  background: #f3eefe;
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
  min-width: 140px;
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
  color: #2563eb;
  font-size: 13px;
  background: #eff6ff;
  border-radius: 8px;
  place-items: center;
}

.table-doc-link {
  overflow: hidden;
  max-width: 190px;
  color: #6040c5;
  font-size: 12px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.hours-cell {
  color: var(--text-color, #17153c);
  font-weight: 650;
}

.billable-cell {
  color: #2563eb;
  font-weight: 600;
}

.amount-cell {
  font-weight: 650;
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
