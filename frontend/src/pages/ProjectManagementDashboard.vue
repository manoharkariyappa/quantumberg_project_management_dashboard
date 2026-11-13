<script setup>
import { computed, onMounted, ref } from "vue";
import {
  Activity,
  CircleAlert,
  ClipboardList,
  FolderKanban,
} from "lucide-vue-next";

import DashboardHeader from "../components/header/DashboardHeader.vue";
import MetricCard from "../components/cards/MetricCard.vue";
import DashboardChart from "../components/charts/DashboardChart.vue";

import ProjectTable from "../components/reports/ProjectTable.vue";
import TaskOverview from "../components/reports/TaskOverview.vue";
import TimesheetOverview from "../components/reports/TimesheetOverview.vue";
import ProjectDeadlines from "../components/reports/ProjectDeadlines.vue";
import AccountingEntries from "../components/reports/AccountingEntries.vue";
import ProjectHealth from "../components/reports/ProjectHealth.vue";
import TeamWorkload from "../components/reports/TeamWorkload.vue";

import {
  getDashboardData,
  getToday,
  openDocument,
  openList,
  openNewDocument,
  openQueryReport,
} from "../services/api.js";
import {
  formatNumber,
  formatTimestamp,
  toNumber,
} from "../utils/formatters.js";

const loading = ref(false);
const errorMessage = ref("");
const lastUpdated = ref("");

const currency = ref("INR");

const access = ref({
  role: "project_user",
  is_admin: false,
  is_manager: false,
  is_project_user: true,
  can_view_finance: false,
  can_view_accounting: false,
  can_view_team: false,
  can_create_project: false,
});

const showFinance = computed(() => Boolean(access.value.can_view_finance));

const dateRange = ref({
  from_date: "",
  to_date: "",
});

const metrics = ref({
  total_projects: 0,
  open_projects: 0,
  on_hold_projects: 0,
  completed_projects: 0,
  total_tasks: 0,
  open_tasks: 0,
  completed_tasks: 0,
  overdue_tasks: 0,
  total_budget: 0,
  actual_cost: 0,
  remaining_budget: 0,
});

const projects = ref([]);
const tasks = ref([]);
const timesheetSummary = ref([]);
const deadlines = ref([]);
const accountingEntries = ref([]);

const projectStatuses = ref([]);
const taskStatuses = ref([]);
const budgetProjects = ref([]);
const costBreakdown = ref([]);
const priorityBreakdown = ref([]);
const monthlyTrend = ref([]);
const projectHealth = ref([]);
const teamWorkload = ref([]);

const statusColors = [
  "#493b91",
  "#c43f9d",
  "#3987f5",
  "#20bf88",
  "#ffad19",
  "#e5484d",
  "#0f9f8f",
  "#78809b",
];

const kpiCards = [
  {
    title: "Total Projects",
    icon: FolderKanban,
    tone: "purple",
    getValue: (m) => formatNumber(m.total_projects),
    getSubtitle: (m) =>
      `${formatNumber(m.open_projects)} active · ${formatNumber(
        m.completed_projects
      )} completed · ${formatNumber(m.on_hold_projects)} on hold`,
    route: () => openList("Project"),
  },
  {
    title: "Active Projects",
    icon: Activity,
    tone: "green",
    getValue: (m) => formatNumber(m.open_projects),
    getSubtitle: (m) => `${formatNumber(m.open_tasks)} open tasks`,
    route: () => openList("Project", { status: "Open" }),
  },
  {
    title: "Total Tasks",
    icon: ClipboardList,
    tone: "blue",
    getValue: (m) => formatNumber(m.total_tasks),
    getSubtitle: (m) =>
      `${formatNumber(m.completed_tasks)} completed · ${formatNumber(
        m.overdue_tasks
      )} overdue`,
    route: () => openList("Task"),
  },
  {
    title: "Overdue Tasks",
    icon: CircleAlert,
    tone: "red",
    getValue: (m) => formatNumber(m.overdue_tasks),
    getSubtitle: () => "Past their due date",
    route: () =>
      openList("Task", {
        status: ["not in", ["Completed", "Cancelled"]],
        exp_end_date: ["<", getToday()],
      }),
  },
];

const visibleKpiCards = computed(() =>
  kpiCards.filter((card) => !card.finance || showFinance.value)
);

const projectStatusChart = {
  title: "Project Status",
  subtitle: "Distribution of projects by status",
  type: "pie",
  valueFormat: "number",
  emptyText: "No projects found.",
};

const taskStatusChart = {
  title: "Task Status",
  subtitle: "Distribution of tasks by status",
  type: "pie",
  valueFormat: "number",
  emptyText: "No tasks found.",
};

const budgetChart = {
  title: "Budget vs Actual Cost",
  subtitle: "Top projects by estimated costing",
  type: "bar",
  colors: ["#493b91", "#c43f9d"],
  series: [
    { name: "Budget", key: "budget" },
    { name: "Actual Cost", key: "actual_cost" },
  ],
  emptyText: "No project budget data available.",
};

const costBreakdownChart = {
  title: "Project Cost Breakdown",
  subtitle: "Cost components across all projects",
  type: "donut",
  valueFormat: "compact",
  emptyText: "No cost data available.",
};

const monthlyTrendChart = {
  title: "Activity Trend",
  subtitle: "Tasks created vs completed over the selected period",
  type: "area",
  valueFormat: "number",
  colors: ["#6040c5", "#20bf88", "#ffad19"],
  series: [
    { name: "Tasks Created", key: "tasks_created" },
    { name: "Tasks Completed", key: "tasks_completed" },
    { name: "Projects Created", key: "projects_created" },
  ],
  emptyText: "No activity found for this period.",
};

const priorityChart = {
  title: "Task Priority Mix",
  subtitle: "Distribution of tasks by priority",
  type: "donut",
  valueFormat: "number",
  colors: ["#e5484d", "#ffad19", "#3987f5", "#78809b"],
  emptyText: "No task priority data available.",
};

async function loadDashboard() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const data = await getDashboardData({
      from_date: dateRange.value.from_date || undefined,
      to_date: dateRange.value.to_date || undefined,
    });

    if (data?.currency) {
      currency.value = data.currency;
    }

    if (data?.access) {
      access.value = {
        ...access.value,
        ...data.access,
      };
    }

    metrics.value = {
      ...metrics.value,
      ...(data?.metrics || {}),
    };

    projects.value = data?.projects || [];
    tasks.value = data?.tasks || [];
    timesheetSummary.value = data?.timesheet_summary || [];
    deadlines.value = data?.deadlines || [];
    accountingEntries.value = data?.accounting_entries || [];

    projectStatuses.value = data?.project_statuses || [];
    taskStatuses.value = data?.task_statuses || [];
    budgetProjects.value = data?.budget_projects || [];
    costBreakdown.value = data?.cost_breakdown || [];
    priorityBreakdown.value = data?.priority_breakdown || [];
    monthlyTrend.value = data?.monthly_trend || [];
    projectHealth.value = data?.project_health || [];
    teamWorkload.value = data?.team_workload || [];

    lastUpdated.value = formatTimestamp();
  } catch (error) {
    console.error("Dashboard loading failed:", error);

    errorMessage.value = error?.message || "Unable to load dashboard data.";
  } finally {
    loading.value = false;
  }
}

function handleDateChange(range) {
  dateRange.value = {
    from_date: range?.from_date || "",
    to_date: range?.to_date || "",
  };

  loadDashboard();
}

function createProject() {
  openNewDocument("Project");
}

function openProjectsList() {
  openList("Project");
}

function openTasksList() {
  openList("Task");
}

function openProjectStatus(record) {
  if (!record?.label) {
    openProjectsList();
    return;
  }

  openList("Project", { status: record.label });
}

function openTaskStatus(record) {
  if (!record?.label) {
    openTasksList();
    return;
  }

  openList("Task", { status: record.label });
}

function openTaskPriority(record) {
  if (!record?.label) {
    openTasksList();
    return;
  }

  openList("Task", { priority: record.label });
}

function openBudgetProject(record) {
  const project = budgetProjects.value.find(
    (item) => item.project_name === record?.label
  );

  if (project) {
    openProject(project);
    return;
  }

  openProjectsList();
}

function openCostBreakdown(record) {
  const routes = {
    "Estimated Costing": "Project",
    "Material Consumed": "Stock Entry",
    "Timesheet Costing": "Timesheet",
    "Billed Amount": "Sales Invoice",
  };

  const doctype = routes[record?.label];

  if (doctype) {
    openList(doctype);
    return;
  }

  openProjectsList();
}

function openTeamMemberTasks(member) {
  if (!member?.user) {
    openTasksList();
    return;
  }

  openList("Task", { _assign: ["like", `%${member.user}%`] });
}

function openProject(project) {
  if (!project?.name) return;

  openDocument("Project", project.name);
}

function openTask(task) {
  if (!task?.name) return;

  openDocument("Task", task.name);
}

function openDeadlineRecord(record) {
  if (!record?.name || !record?.doctype) return;

  openDocument(record.doctype, record.name);
}

function openAccountingList() {
  openQueryReport("General Ledger", {
    from_date: dateRange.value.from_date,
    to_date: dateRange.value.to_date,
    group_by: "Project",
  });
}

function openAccountingEntry(entry) {
  if (!entry?.name) return;

  openDocument(entry.voucher_type || entry.doctype, entry.name);
}

onMounted(loadDashboard);
</script>

<template>
  <main class="project-dashboard">
    <DashboardHeader
      :from-date="dateRange.from_date"
      :to-date="dateRange.to_date"
      :loading="loading"
      :last-updated="lastUpdated"
      :can-create="access.can_create_project"
      @date-change="handleDateChange"
      @refresh="loadDashboard"
      @new-project="createProject"
    />

    <div v-if="errorMessage" class="error-banner">
      <span>{{ errorMessage }}</span>
      <button @click="loadDashboard">Retry</button>
    </div>

    <!-- KPI cards -->
    <section class="dashboard-grid dashboard-grid--kpis">
      <MetricCard
        v-for="card in visibleKpiCards"
        :key="card.title"
        :title="card.title"
        :icon="card.icon"
        :tone="card.tone"
        :value="card.getValue(metrics)"
        :subtitle="card.getSubtitle(metrics)"
        :loading="loading"
        :clickable="Boolean(card.route)"
        @select="card.route && card.route()"
      />
    </section>

    <!-- Charts -->
    <section class="dashboard-grid dashboard-grid--charts">
      <DashboardChart
        class="chart-span-full"
        :title="monthlyTrendChart.title"
        :subtitle="monthlyTrendChart.subtitle"
        :type="monthlyTrendChart.type"
        :value-format="monthlyTrendChart.valueFormat"
        :colors="monthlyTrendChart.colors"
        :empty-text="monthlyTrendChart.emptyText"
        :labels="monthlyTrend.map((item) => item.label)"
        :series="
          monthlyTrendChart.series.map((serie) => ({
            name: serie.name,
            data: monthlyTrend.map((item) => toNumber(item[serie.key])),
          }))
        "
        :loading="loading"
        view-all-label="Tasks"
        @open-report="openTasksList"
      />

      <DashboardChart
        v-if="showFinance"
        class="chart-span-2"
        :title="budgetChart.title"
        :subtitle="budgetChart.subtitle"
        :type="budgetChart.type"
        :colors="budgetChart.colors"
        :currency="currency"
        :empty-text="budgetChart.emptyText"
        :labels="budgetProjects.map((item) => item.project_name)"
        :series="budgetChart.series.map((serie) => ({
          name: serie.name,
          data: budgetProjects.map((item) => toNumber(item[serie.key])),
        }))"
        :loading="loading"
        view-all-label="All Projects"
        @open-report="openProjectsList"
        @open-record="openBudgetProject"
      />

      <DashboardChart
        :title="projectStatusChart.title"
        :subtitle="projectStatusChart.subtitle"
        :type="projectStatusChart.type"
        :value-format="projectStatusChart.valueFormat"
        :empty-text="projectStatusChart.emptyText"
        :labels="projectStatuses.map((item) => item.name)"
        :series="projectStatuses.map((item) => toNumber(item.count))"
        :colors="statusColors"
        :loading="loading"
        view-all-label="Projects"
        @open-report="openProjectsList"
        @open-record="openProjectStatus"
      />

      <DashboardChart
        :title="taskStatusChart.title"
        :subtitle="taskStatusChart.subtitle"
        :type="taskStatusChart.type"
        :value-format="taskStatusChart.valueFormat"
        :empty-text="taskStatusChart.emptyText"
        :labels="taskStatuses.map((item) => item.name)"
        :series="taskStatuses.map((item) => toNumber(item.count))"
        :colors="statusColors"
        :loading="loading"
        view-all-label="Tasks"
        @open-report="openTasksList"
        @open-record="openTaskStatus"
      />

      <DashboardChart
        v-if="showFinance"
        :title="costBreakdownChart.title"
        :subtitle="costBreakdownChart.subtitle"
        :type="costBreakdownChart.type"
        :value-format="costBreakdownChart.valueFormat"
        :currency="currency"
        :empty-text="costBreakdownChart.emptyText"
        :labels="costBreakdown.map((item) => item.name)"
        :series="costBreakdown.map((item) => toNumber(item.amount))"
        :colors="statusColors"
        :loading="loading"
        view-all-label="Projects"
        @open-report="openProjectsList"
        @open-record="openCostBreakdown"
      />

      <DashboardChart
        :title="priorityChart.title"
        :subtitle="priorityChart.subtitle"
        :type="priorityChart.type"
        :value-format="priorityChart.valueFormat"
        :empty-text="priorityChart.emptyText"
        :labels="priorityBreakdown.map((item) => item.name)"
        :series="priorityBreakdown.map((item) => toNumber(item.count))"
        :colors="priorityChart.colors"
        :loading="loading"
        view-all-label="Tasks"
        @open-report="openTasksList"
        @open-record="openTaskPriority"
      />
    </section>

    <!-- Project health and team workload -->
    <section
      class="dashboard-grid dashboard-grid--tables"
      :class="{ 'dashboard-grid--single': !access.can_view_team }"
    >
      <ProjectHealth
        :projects="projectHealth"
        :loading="loading"
        :currency="currency"
        :show-finance="showFinance"
        @open-project="openProject"
        @open-all="openProjectsList"
      />

      <TeamWorkload
        v-if="access.can_view_team"
        :members="teamWorkload"
        :loading="loading"
        @open-tasks="openTeamMemberTasks"
      />
    </section>

    <!-- Projects and accounting -->
    <section
      class="dashboard-grid dashboard-grid--tables"
      :class="{ 'dashboard-grid--single': !access.can_view_accounting }"
    >
      <ProjectTable
        :projects="projects"
        :loading="loading"
        :currency="currency"
        :show-finance="showFinance"
        @view-all="openProjectsList"
        @open-project="openProject"
      />

      <AccountingEntries
        v-if="access.can_view_accounting"
        :entries="accountingEntries"
        :loading="loading"
        :currency="currency"
        @view-all="openAccountingList"
        @open-entry="openAccountingEntry"
      />
    </section>

    <!-- Timesheets and deadlines -->
    <section class="dashboard-grid dashboard-grid--tables">
      <TimesheetOverview
        :projects="timesheetSummary"
        :loading="loading"
        :currency="currency"
        :show-finance="showFinance"
        @open-project="openProject"
      />

      <ProjectDeadlines
        :records="deadlines"
        :loading="loading"
        @open-record="openDeadlineRecord"
      />
    </section>

    <!-- Task overview -->
    <section class="dashboard-section">
      <TaskOverview
        :tasks="tasks"
        :loading="loading"
        @open-task="openTask"
      />
    </section>

    <footer class="dashboard-footer">
      <span>Project Management · Tasks · Timesheets · Finance</span>
      <span v-if="lastUpdated">Updated {{ lastUpdated }}</span>
    </footer>
  </main>
</template>

<style scoped>
.project-dashboard {
  width: 100%;
  max-width: 1600px;
  min-width: 0;
  margin: 0 auto;
  padding: 16px;
  color: var(--text-color, #333333);
  font-family: var(--font-stack, inherit);
  font-size: 14px;
  line-height: 1.5;
}

.error-banner {
  display: flex;
  gap: 11px;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  margin-top: 12px;
  color: #9f1239;
  font-size: 12px;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 10px;
}

@media (max-width: 700px) {
  .project-dashboard {
    padding: 10px;
  }
}
</style>
