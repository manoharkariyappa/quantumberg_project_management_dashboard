import json

import frappe
from frappe.utils import (
	add_days,
	add_months,
	flt,
	get_first_day,
	get_last_day,
	getdate,
	nowdate,
)

OPEN_TASK_STATUSES = ["Open", "Working", "Pending Review", "Overdue"]
CLOSED_TASK_STATUSES = ["Completed", "Cancelled"]
TASK_FIELDS = [
	"name",
	"subject",
	"project",
	"status",
	"priority",
	"exp_end_date",
	"exp_start_date",
	"is_milestone",
	"owner",
	"_assign",
	"progress",
	"creation",
]
PROJECT_FINANCE_FIELDS = [
	"estimated_costing",
	"total_purchase_cost",
	"total_consumed_material_cost",
	"total_costing_amount",
	"total_billable_amount",
	"total_billed_amount",
]

ADMIN_ROLES = {"System Manager", "Administrator"}
MANAGER_ROLES = {"Projects Manager"}


def _has_doctype(doctype):
	return bool(frappe.db.exists("DocType", doctype))


def _user_project_names(user):
	"""Return projects where the user is a team member (Project Users table) or owner."""
	projects = set()

	if _has_doctype("Project User"):
		projects.update(
			frappe.get_all(
				"Project User",
				filters={"parenttype": "Project", "user": user},
				pluck="parent",
				limit_page_length=0,
			)
		)

	if _has_doctype("Project"):
		projects.update(
			frappe.get_all(
				"Project",
				filters={"owner": user},
				pluck="name",
				limit_page_length=0,
			)
		)

	return {project for project in projects if project}


def _get_access():
	"""Resolve the current user's dashboard role and data scope."""
	user = frappe.session.user or "Guest"
	roles = set(frappe.get_roles(user))

	is_admin = user == "Administrator" or bool(roles & ADMIN_ROLES)
	is_manager = bool(roles & MANAGER_ROLES)
	is_project_user = not is_admin and not is_manager

	if is_admin:
		role = "admin"
		projects = None
	elif is_manager:
		role = "manager"
		projects = None
	else:
		role = "project_user"
		projects = _user_project_names(user)

	return {
		"user": user,
		"role": role,
		"roles": sorted(roles),
		"is_admin": is_admin,
		"is_manager": is_manager,
		"is_project_user": is_project_user,
		"can_view_finance": is_admin or is_manager,
		"can_view_accounting": is_admin or is_manager,
		"can_view_team": is_admin or is_manager,
		"can_create_project": is_admin or is_manager,
		"projects": projects,
	}


def _access():
	access = getattr(frappe.local, "qb_project_access", None)

	if access is None:
		access = _get_access()
		frappe.local.qb_project_access = access

	return access


def _scope_projects():
	"""None means unrestricted, otherwise a set of allowed project names."""
	return _access().get("projects")


def _project_scope_sql(column="name", param="scope_projects"):
	"""Return a SQL fragment and params scoping a query to allowed projects."""
	projects = _scope_projects()

	if projects is None:
		return "", {}

	if not projects:
		return " AND 1 = 0", {}

	return f" AND {column} IN %({param})s", {param: tuple(projects)}


def _project_scope_filter(field="name"):
	projects = _scope_projects()

	if projects is None:
		return {}

	return {field: ["in", list(projects)]}


def _restricted():
	return _scope_projects() is not None


def _no_projects():
	projects = _scope_projects()

	return projects is not None and not projects


def _count(doctype, filters=None):
	if not _has_doctype(doctype):
		return 0

	return frappe.db.count(doctype, filters=filters or {})


def _date_range(from_date=None, to_date=None):
	"""Resolve the dashboard date range, defaulting to the last 365 days."""
	end = getdate(nowdate())
	start = add_days(end, -365)

	try:
		if from_date:
			start = getdate(from_date)
		if to_date:
			end = getdate(to_date)
	except Exception:
		pass

	if end < start:
		start, end = end, start

	return start, end


def _actual_cost(row):
	return flt(row.get("total_purchase_cost")) + flt(row.get("total_consumed_material_cost")) + flt(
		row.get("total_costing_amount")
	)


def _get_currency():
	try:
		return frappe.defaults.get_global_default("currency") or "INR"
	except Exception:
		return "INR"


def _project_manager_map():
	"""Map project -> first team member full name from the Project users table."""
	if not _has_doctype("Project User"):
		return {}

	users = frappe.get_all(
		"Project User",
		filters={"parenttype": "Project"},
		fields=["parent", "full_name", "user"],
		order_by="idx asc",
		limit_page_length=0,
	)

	managers = {}
	for row in users:
		if row.parent and row.parent not in managers:
			managers[row.parent] = row.full_name or row.user or ""

	return managers


def _user_name_map(rows):
	"""Resolve user ids referenced by tasks (assignees / owners) to full names."""
	ids = set()

	for row in rows:
		for field in ("assigned_to", "owner"):
			value = row.get(field)
			if value:
				ids.add(value)

	if not ids or not _has_doctype("User"):
		return {}

	users = frappe.get_all(
		"User",
		filters={"name": ["in", sorted(ids)]},
		fields=["name", "full_name"],
		limit_page_length=0,
	)

	return {user.name: user.full_name or user.name for user in users}


def _get_metrics():
	projects_exist = _has_doctype("Project")
	tasks_exist = _has_doctype("Task")

	project_filters = {"docstatus": ["<", 2]}
	task_filters = {"docstatus": ["<", 2]}
	project_filters.update(_project_scope_filter("name"))
	task_filters.update(_project_scope_filter("project"))

	total_projects = _count("Project", project_filters)
	open_projects = _count("Project", {**project_filters, "status": "Open"})
	on_hold_projects = _count("Project", {**project_filters, "status": "On Hold"})
	completed_projects = _count("Project", {**project_filters, "status": "Completed"})

	total_tasks = _count("Task", task_filters)
	open_tasks = _count("Task", {**task_filters, "status": ["in", OPEN_TASK_STATUSES]})
	completed_tasks = _count("Task", {**task_filters, "status": "Completed"})
	overdue_tasks = _count(
		"Task",
		{**task_filters, "status": ["in", OPEN_TASK_STATUSES], "exp_end_date": ["<", nowdate()]},
	)

	total_budget = 0
	actual_cost = 0
	total_billed = 0

	if projects_exist:
		scope_sql, scope_params = _project_scope_sql("name")
		finance = frappe.db.sql(
			f"""
			SELECT
				COALESCE(SUM(estimated_costing), 0) AS total_budget,
				COALESCE(SUM(total_purchase_cost + total_consumed_material_cost
					+ total_costing_amount), 0) AS actual_cost,
				COALESCE(SUM(total_billed_amount), 0) AS total_billed
			FROM `tabProject`
			WHERE docstatus < 2 {scope_sql}
			""",
			scope_params,
			as_dict=True,
		)

		if finance:
			total_budget = flt(finance[0].total_budget)
			actual_cost = flt(finance[0].actual_cost)
			total_billed = flt(finance[0].total_billed)

	return {
		"total_projects": total_projects,
		"open_projects": open_projects,
		"on_hold_projects": on_hold_projects,
		"completed_projects": completed_projects,
		"total_tasks": total_tasks,
		"open_tasks": open_tasks,
		"completed_tasks": completed_tasks,
		"overdue_tasks": overdue_tasks,
		"total_budget": total_budget,
		"actual_cost": actual_cost,
		"remaining_budget": total_budget - actual_cost,
		"total_billed": total_billed,
		"has_projects_module": projects_exist and tasks_exist,
	}


def _get_project_statuses():
	if not _has_doctype("Project"):
		return []

	rows = frappe.db.sql(
		f"""
		SELECT status, COUNT(*) AS total
		FROM `tabProject`
		WHERE docstatus < 2 {_project_scope_sql("name")[0]}
		GROUP BY status
		ORDER BY total DESC
		""",
		_project_scope_sql("name")[1],
		as_dict=True,
	)

	return [{"name": row.status or "Unknown", "count": row.total} for row in rows]


def _get_task_statuses():
	if not _has_doctype("Task"):
		return []

	rows = frappe.db.sql(
		f"""
		SELECT status, COUNT(*) AS total
		FROM `tabTask`
		WHERE docstatus < 2 {_project_scope_sql("project")[0]}
		GROUP BY status
		ORDER BY total DESC
		""",
		_project_scope_sql("project")[1],
		as_dict=True,
	)

	return [{"name": row.status or "Unknown", "count": row.total} for row in rows]


def _get_budget_projects():
	if not _has_doctype("Project"):
		return []

	rows = frappe.get_all(
		"Project",
		filters={"docstatus": ["<", 2], **_project_scope_filter("name")},
		fields=["name", "project_name", *PROJECT_FINANCE_FIELDS],
		order_by="estimated_costing desc",
		limit_page_length=6,
	)

	budget_projects = []

	for row in rows:
		budget = flt(row.estimated_costing)
		actual = _actual_cost(row)

		if not budget and not actual:
			continue

		label = (row.project_name or row.name or "").strip()
		budget_projects.append(
			{
				"name": row.name,
				"project_name": label,
				"label": label[:14] if len(label) > 14 else label,
				"budget": budget,
				"actual_cost": actual,
			}
		)

	return budget_projects


def _get_cost_breakdown():
	if not _has_doctype("Project"):
		return []

	scope_sql, scope_params = _project_scope_sql("name")
	row = frappe.db.sql(
		f"""
		SELECT
			COALESCE(SUM(estimated_costing), 0) AS estimated,
			COALESCE(SUM(total_purchase_cost), 0) AS purchase,
			COALESCE(SUM(total_consumed_material_cost), 0) AS material,
			COALESCE(SUM(total_costing_amount), 0) AS timesheet,
			COALESCE(SUM(total_billed_amount), 0) AS billed
		FROM `tabProject`
		WHERE docstatus < 2 {scope_sql}
		""",
		scope_params,
		as_dict=True,
	)

	if not row:
		return []

	row = row[0]

	breakdown = [
		{"name": "Estimated Costing", "amount": flt(row.estimated)},
		{"name": "Purchase Cost", "amount": flt(row.purchase)},
		{"name": "Material Consumed", "amount": flt(row.material)},
		{"name": "Timesheet Costing", "amount": flt(row.timesheet)},
		{"name": "Billed Amount", "amount": flt(row.billed)},
	]

	return [item for item in breakdown if item["amount"]]


def _get_recent_projects():
	if not _has_doctype("Project"):
		return []

	rows = frappe.get_all(
		"Project",
		filters={"docstatus": ["<", 2], **_project_scope_filter("name")},
		fields=[
			"name",
			"project_name",
			"status",
			"priority",
			"customer",
			"project_type",
			"percent_complete",
			"expected_start_date",
			"expected_end_date",
			*PROJECT_FINANCE_FIELDS,
			"creation",
		],
		order_by="creation desc",
		limit_page_length=15,
	)

	managers = _project_manager_map()

	projects = []

	for row in rows:
		projects.append(
			{
				"name": row.name,
				"project_name": row.project_name or row.name,
				"project_manager": managers.get(row.name, ""),
				"status": row.status,
				"priority": row.priority,
				"customer": row.customer,
				"project_type": row.project_type,
				"percent_complete": flt(row.percent_complete),
				"expected_start_date": row.expected_start_date,
				"expected_end_date": row.expected_end_date,
				"budget": flt(row.estimated_costing),
				"actual_cost": _actual_cost(row),
				"total_billed": flt(row.total_billed_amount),
			}
		)

	return projects


def _get_tasks(start_date, end_date):
	if not _has_doctype("Task"):
		return []

	scope_filter = _project_scope_filter("project")

	open_tasks = frappe.get_all(
		"Task",
		filters={"docstatus": ["<", 2], "status": ["in", OPEN_TASK_STATUSES], **scope_filter},
		fields=TASK_FIELDS,
		order_by="exp_end_date asc",
		limit_page_length=30,
	)

	recent_tasks = frappe.get_all(
		"Task",
		filters={
			"docstatus": ["<", 2],
			"creation": ["between", [str(start_date), str(end_date) + " 23:59:59"]],
			**scope_filter,
		},
		fields=TASK_FIELDS,
		order_by="creation desc",
		limit_page_length=30,
	)

	today = getdate(nowdate())
	merged = {}

	for row in open_tasks + recent_tasks:
		if row.name not in merged:
			exp_end = getdate(row.exp_end_date) if row.exp_end_date else None

			assignees = []
			if row.get("_assign"):
				try:
					assignees = json.loads(row._assign)
				except Exception:
					assignees = []

			merged[row.name] = {
				"name": row.name,
				"subject": row.subject,
				"project": row.project,
				"status": row.status,
				"priority": row.priority,
				"exp_end_date": row.exp_end_date,
				"exp_start_date": row.exp_start_date,
				"is_milestone": bool(row.is_milestone),
				"progress": flt(row.progress),
				"owner": row.owner or "",
				"assigned_to": assignees[0] if assignees else (row.owner or ""),
				"is_overdue": bool(exp_end and exp_end < today and row.status in OPEN_TASK_STATUSES),
			}

	tasks = sorted(
		merged.values(),
		key=lambda task: (
			not task["is_overdue"],
			str(task["exp_end_date"] or "9999-12-31"),
			task["name"],
		),
	)

	tasks = tasks[:15]

	name_map = _user_name_map(tasks)

	for task in tasks:
		for field in ("assigned_to", "owner"):
			if task.get(field):
				task[field] = name_map.get(task[field], task[field])

	return tasks


def _get_timesheet_summary(start_date, end_date):
	if not _has_doctype("Timesheet Detail"):
		return []

	scope_sql, scope_params = _project_scope_sql("td.project")
	rows = frappe.db.sql(
		f"""
		SELECT
			td.project AS project,
			p.project_name AS project_name,
			p.status AS status,
			SUM(td.hours) AS total_hours,
			SUM(td.billing_hours) AS billable_hours,
			SUM(td.costing_amount) AS costing_amount,
			SUM(td.billing_amount) AS billing_amount
		FROM `tabTimesheet Detail` td
		INNER JOIN `tabTimesheet` ts ON ts.name = td.parent AND ts.docstatus < 2
		LEFT JOIN `tabProject` p ON p.name = td.project
		WHERE IFNULL(td.project, '') != ''
			AND ts.start_date BETWEEN %(start_date)s AND %(end_date)s {scope_sql}
		GROUP BY td.project, p.project_name, p.status
		ORDER BY total_hours DESC
		LIMIT 10
		""",
		{"start_date": start_date, "end_date": end_date, **scope_params},
		as_dict=True,
	)

	return [
		{
			"project": row.project,
			"project_name": row.project_name or row.project,
			"status": row.status or "Open",
			"total_hours": flt(row.total_hours, 2),
			"billable_hours": flt(row.billable_hours, 2),
			"costing_amount": flt(row.costing_amount),
			"billing_amount": flt(row.billing_amount),
		}
		for row in rows
	]


def _get_deadlines():
	deadlines = []

	if _has_doctype("Project"):
		projects = frappe.get_all(
			"Project",
			filters={
				"docstatus": ["<", 2],
				"status": ["in", ["Open", "On Hold"]],
				"expected_end_date": ["is", "set"],
				**_project_scope_filter("name"),
			},
			fields=["name", "project_name", "status", "expected_end_date", "percent_complete"],
			order_by="expected_end_date asc",
			limit_page_length=10,
		)

		for row in projects:
			deadlines.append(
				{
					"name": row.name,
					"doctype": "Project",
					"title": row.project_name or row.name,
					"due_date": row.expected_end_date,
					"status": row.status,
					"progress": flt(row.percent_complete),
				}
			)

	if _has_doctype("Task"):
		milestones = frappe.get_all(
			"Task",
			filters={
				"docstatus": ["<", 2],
				"is_milestone": 1,
				"status": ["in", OPEN_TASK_STATUSES],
				"exp_end_date": ["is", "set"],
				**_project_scope_filter("project"),
			},
			fields=["name", "subject", "status", "exp_end_date", "project"],
			order_by="exp_end_date asc",
			limit_page_length=10,
		)

		for row in milestones:
			deadlines.append(
				{
					"name": row.name,
					"doctype": "Task",
					"title": row.subject or row.name,
					"due_date": row.exp_end_date,
					"status": row.status,
					"project": row.project,
				}
			)

	return deadlines


def _get_accounting_entries(start_date, end_date):
	if not _has_doctype("GL Entry") or not _access()["can_view_accounting"]:
		return []

	scope_sql, scope_params = _project_scope_sql("project")
	rows = frappe.db.sql(
		f"""
		SELECT
			voucher_type,
			voucher_no,
			posting_date,
			project,
			account,
			party,
			remarks,
			debit,
			credit
		FROM `tabGL Entry`
		WHERE docstatus = 1
			AND is_cancelled = 0
			AND IFNULL(project, '') != ''
			AND posting_date BETWEEN %(start_date)s AND %(end_date)s {scope_sql}
		ORDER BY posting_date DESC, creation DESC
		LIMIT 15
		""",
		{"start_date": start_date, "end_date": end_date, **scope_params},
		as_dict=True,
	)

	return [
		{
			"name": row.voucher_no,
			"voucher_type": row.voucher_type,
			"doctype": row.voucher_type,
			"posting_date": row.posting_date,
			"project": row.project,
			"account": row.account,
			"party": row.party,
			"reference": row.voucher_no,
			"remarks": row.remarks,
			"debit": flt(row.debit),
			"credit": flt(row.credit),
			"status": "Submitted",
		}
		for row in rows
	]


def _get_priority_breakdown():
	if not _has_doctype("Task"):
		return []

	scope_sql, scope_params = _project_scope_sql("project")
	rows = frappe.db.sql(
		f"""
		SELECT COALESCE(NULLIF(priority, ''), 'Medium') AS priority,
			COUNT(*) AS total
		FROM `tabTask`
		WHERE docstatus < 2 {scope_sql}
		GROUP BY priority
		ORDER BY total DESC
		""",
		scope_params,
		as_dict=True,
	)

	return [{"name": row.priority or "Medium", "count": row.total} for row in rows]


def _month_rows(sql, params):
	return {row.ym: row for row in frappe.db.sql(sql, params, as_dict=True) if row.ym}


def _get_monthly_trend(start_date, end_date):
	"""Return a month-by-month activity series for the dashboard charts."""
	start = get_first_day(start_date)
	end = getdate(end_date)
	cursor = get_first_day(end)
	months = []

	while cursor >= start and len(months) < 12:
		months.append(cursor)
		cursor = get_first_day(add_months(cursor, -1))

	months.reverse()

	if not months:
		return []

	params = {
		"start": str(months[0]),
		"end": str(get_last_day(end)) + " 23:59:59",
	}
	task_scope_sql, scope_params = _project_scope_sql("project")
	project_scope_sql, _ = _project_scope_sql("name")
	timesheet_scope_sql, _ = _project_scope_sql("td.project")
	params.update(scope_params)
	tasks_created = {}
	tasks_completed = {}
	projects_created = {}
	timesheets = {}

	if _has_doctype("Task"):
		tasks_created = _month_rows(
			f"""
			SELECT DATE_FORMAT(creation, '%%Y-%%m') AS ym, COUNT(*) AS total
			FROM `tabTask`
			WHERE docstatus < 2 AND creation BETWEEN %(start)s AND %(end)s {task_scope_sql}
			GROUP BY ym
			""",
			params,
		)
		tasks_completed = _month_rows(
			f"""
			SELECT DATE_FORMAT(completed_on, '%%Y-%%m') AS ym, COUNT(*) AS total
			FROM `tabTask`
			WHERE docstatus < 2 AND completed_on IS NOT NULL
				AND completed_on BETWEEN %(start)s AND %(end)s {task_scope_sql}
			GROUP BY ym
			""",
			params,
		)

	if _has_doctype("Project"):
		projects_created = _month_rows(
			f"""
			SELECT DATE_FORMAT(creation, '%%Y-%%m') AS ym, COUNT(*) AS total
			FROM `tabProject`
			WHERE docstatus < 2 AND creation BETWEEN %(start)s AND %(end)s {project_scope_sql}
			GROUP BY ym
			""",
			params,
		)

	if _has_doctype("Timesheet Detail"):
		timesheets = _month_rows(
			f"""
			SELECT DATE_FORMAT(ts.start_date, '%%Y-%%m') AS ym,
				SUM(td.hours) AS hours,
				SUM(td.costing_amount) AS cost,
				SUM(td.billing_amount) AS billing
			FROM `tabTimesheet Detail` td
			INNER JOIN `tabTimesheet` ts ON ts.name = td.parent AND ts.docstatus < 2
			WHERE ts.start_date BETWEEN %(start)s AND %(end)s {timesheet_scope_sql}
			GROUP BY ym
			""",
			params,
		)

	trend = []

	for month in months:
		key = month.strftime("%Y-%m")
		ts = timesheets.get(key)
		trend.append(
			{
				"label": month.strftime("%b %y"),
				"month": key,
				"projects_created": projects_created.get(key).total if projects_created.get(key) else 0,
				"tasks_created": tasks_created.get(key).total if tasks_created.get(key) else 0,
				"tasks_completed": tasks_completed.get(key).total if tasks_completed.get(key) else 0,
				"hours": flt(ts.hours, 2) if ts else 0,
				"cost": flt(ts.cost) if ts else 0,
				"billing": flt(ts.billing) if ts else 0,
			}
		)

	return trend


def _get_project_health():
	"""Derive a simple health signal for every project (budget + schedule + tasks)."""
	if not _has_doctype("Project"):
		return []

	projects = frappe.get_all(
		"Project",
		filters={"docstatus": ["<", 2], **_project_scope_filter("name")},
		fields=[
			"name",
			"project_name",
			"status",
			"priority",
			"percent_complete",
			"expected_end_date",
			*PROJECT_FINANCE_FIELDS,
		],
		limit_page_length=0,
	)

	task_stats = {}

	if _has_doctype("Task"):
		scope_sql, scope_params = _project_scope_sql("project")
		rows = frappe.db.sql(
			f"""
			SELECT project,
				COUNT(*) AS total,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed,
				SUM(CASE WHEN status IN ('Open', 'Working', 'Pending Review', 'Overdue')
					THEN 1 ELSE 0 END) AS open_tasks,
				SUM(CASE WHEN status IN ('Open', 'Working', 'Pending Review', 'Overdue')
					AND exp_end_date IS NOT NULL AND exp_end_date < CURDATE()
					THEN 1 ELSE 0 END) AS overdue
			FROM `tabTask`
			WHERE docstatus < 2 AND IFNULL(project, '') != '' {scope_sql}
			GROUP BY project
			""",
			scope_params,
			as_dict=True,
		)
		task_stats = {row.project: row for row in rows}

	today = getdate(nowdate())
	health_rows = []

	for project in projects:
		budget = flt(project.estimated_costing)
		actual = _actual_cost(project)
		utilization = (actual / budget * 100) if budget else 0
		completion = flt(project.percent_complete)
		stats = task_stats.get(project.name)

		days_remaining = None
		if project.expected_end_date:
			days_remaining = (getdate(project.expected_end_date) - today).days

		overdue_tasks = stats.overdue if stats else 0
		open_tasks = stats.open_tasks if stats else 0
		completed_tasks = stats.completed if stats else 0

		if project.status == "Completed":
			health = "Completed"
		elif project.status == "Cancelled":
			health = "Cancelled"
		elif days_remaining is not None and days_remaining < 0:
			health = "Overdue"
		elif utilization > 100:
			health = "Over Budget"
		elif overdue_tasks:
			health = "At Risk"
		elif days_remaining is not None and days_remaining <= 14 and completion < 80:
			health = "At Risk"
		elif utilization >= 85:
			health = "Watch"
		else:
			health = "On Track"

		health_rows.append(
			{
				"name": project.name,
				"project_name": project.project_name or project.name,
				"status": project.status,
				"priority": project.priority,
				"health": health,
				"completion": completion,
				"budget": budget,
				"actual_cost": actual,
				"utilization": utilization,
				"days_remaining": days_remaining,
				"open_tasks": open_tasks,
				"completed_tasks": completed_tasks,
				"overdue_tasks": overdue_tasks,
			}
		)

	health_order = {
		"Overdue": 0,
		"At Risk": 1,
		"Over Budget": 2,
		"Watch": 3,
		"On Track": 4,
		"Completed": 5,
		"Cancelled": 6,
	}

	health_rows.sort(
		key=lambda row: (
			health_order.get(row["health"], 9),
			row["days_remaining"] if row["days_remaining"] is not None else 9999,
		)
	)

	return health_rows[:10]


def _get_team_workload():
	"""Aggregate open/completed/overdue tasks and logged hours per team member."""
	if not _has_doctype("Task") or not _access()["can_view_team"]:
		return []

	tasks = frappe.get_all(
		"Task",
		filters={"docstatus": ["<", 2], **_project_scope_filter("project")},
		fields=["name", "status", "priority", "project", "exp_end_date", "_assign", "owner"],
		limit_page_length=0,
	)

	today = getdate(nowdate())
	workload = {}

	for task in tasks:
		assignees = []

		if task.get("_assign"):
			try:
				assignees = json.loads(task._assign) or []
			except Exception:
				assignees = []

		user = assignees[0] if assignees else task.owner

		if not user:
			continue

		member = workload.setdefault(
			user,
			{
				"user": user,
				"open_tasks": 0,
				"completed_tasks": 0,
				"overdue_tasks": 0,
				"total_tasks": 0,
				"projects": set(),
				"hours": 0,
			},
		)

		member["total_tasks"] += 1

		if task.status in OPEN_TASK_STATUSES:
			member["open_tasks"] += 1

			if task.exp_end_date and getdate(task.exp_end_date) < today:
				member["overdue_tasks"] += 1

		if task.status == "Completed":
			member["completed_tasks"] += 1

		if task.project:
			member["projects"].add(task.project)

	if _has_doctype("Timesheet Detail"):
		scope_sql, scope_params = _project_scope_sql("td.project")
		hours = frappe.db.sql(
			f"""
			SELECT ts.user AS user, SUM(td.hours) AS hours
			FROM `tabTimesheet Detail` td
			INNER JOIN `tabTimesheet` ts ON ts.name = td.parent AND ts.docstatus < 2
			WHERE IFNULL(ts.user, '') != '' {scope_sql}
			GROUP BY ts.user
			""",
			scope_params,
			as_dict=True,
		)

		for row in hours:
			member = workload.setdefault(
				row.user,
				{
					"user": row.user,
					"open_tasks": 0,
					"completed_tasks": 0,
					"overdue_tasks": 0,
					"total_tasks": 0,
					"projects": set(),
					"hours": 0,
				},
			)
			member["hours"] = flt(row.hours, 1)

	names = _user_name_map([{"owner": user} for user in workload])

	result = []

	for member in workload.values():
		result.append(
			{
				"user": member["user"],
				"full_name": names.get(member["user"], member["user"]),
				"open_tasks": member["open_tasks"],
				"completed_tasks": member["completed_tasks"],
				"overdue_tasks": member["overdue_tasks"],
				"total_tasks": member["total_tasks"],
				"hours": member["hours"],
				"projects": len(member["projects"]),
			}
		)

	result.sort(key=lambda row: (row["open_tasks"], row["total_tasks"]), reverse=True)

	return result[:8]


def _strip_finance(data):
	"""Remove monetary values for roles that cannot view project finance."""
	metrics = data.get("metrics") or {}

	for key in ("total_budget", "actual_cost", "remaining_budget", "total_billed"):
		metrics[key] = 0

	data["budget_projects"] = []
	data["cost_breakdown"] = []

	for project in data.get("projects") or []:
		project["budget"] = 0
		project["actual_cost"] = 0
		project["total_billed"] = 0

	for project in data.get("project_health") or []:
		project["budget"] = 0
		project["actual_cost"] = 0
		project["utilization"] = 0

	for row in data.get("timesheet_summary") or []:
		row["costing_amount"] = 0
		row["billing_amount"] = 0

	for row in data.get("monthly_trend") or []:
		row["cost"] = 0
		row["billing"] = 0

	return data


@frappe.whitelist()
def get_dashboard_data(from_date=None, to_date=None):
	"""Return every dataset used by the Project Management Dashboard.

	All numbers are fetched live from ERPNext doctypes (Project, Task,
	Timesheet, GL Entry) - nothing is stored or customised by this app.
	"""
	start_date, end_date = _date_range(from_date, to_date)
	access = _get_access()
	frappe.local.qb_project_access = access

	data = {
		"currency": _get_currency(),
		"period": {"from_date": str(start_date), "to_date": str(end_date)},
		"metrics": _get_metrics(),
		"project_statuses": _get_project_statuses(),
		"task_statuses": _get_task_statuses(),
		"budget_projects": _get_budget_projects(),
		"cost_breakdown": _get_cost_breakdown(),
		"projects": _get_recent_projects(),
		"tasks": _get_tasks(start_date, end_date),
		"timesheet_summary": _get_timesheet_summary(start_date, end_date),
		"deadlines": _get_deadlines(),
		"accounting_entries": _get_accounting_entries(start_date, end_date),
		"priority_breakdown": _get_priority_breakdown(),
		"monthly_trend": _get_monthly_trend(start_date, end_date),
		"project_health": _get_project_health(),
		"team_workload": _get_team_workload(),
	}

	if not access["can_view_finance"]:
		data = _strip_finance(data)

	data["access"] = {
		key: value for key, value in access.items() if key not in ("projects", "roles")
	}
	data["access"]["roles"] = access["roles"]
	data["access"]["project_count"] = (
		len(access["projects"]) if access["projects"] is not None else None
	)

	return data
