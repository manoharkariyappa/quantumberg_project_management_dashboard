app_name = "quantumberg_project_management_dashboard"
app_title = "Quantumberg Project Management Dashboard"
app_publisher = "Quantumberg Technologies"
app_description = "Custom Vue.js project management and compliance dashboard for ERPNext"
app_email = "manohar.kariyappa@gmial.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "quantumberg_project_management_dashboard",
# 		"logo": "/assets/quantumberg_project_management_dashboard/logo.png",
# 		"title": "Quantumberg Project Management Dashboard",
# 		"route": "/quantumberg_project_management_dashboard",
# 		"has_permission": "quantumberg_project_management_dashboard.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/quantumberg_project_management_dashboard/css/quantumberg_project_management_dashboard.css"
# app_include_js = "/assets/quantumberg_project_management_dashboard/js/quantumberg_project_management_dashboard.js"

# include js, css files in header of web template
# web_include_css = "/assets/quantumberg_project_management_dashboard/css/quantumberg_project_management_dashboard.css"
# web_include_js = "/assets/quantumberg_project_management_dashboard/js/quantumberg_project_management_dashboard.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "quantumberg_project_management_dashboard/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "quantumberg_project_management_dashboard/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "quantumberg_project_management_dashboard.utils.jinja_methods",
# 	"filters": "quantumberg_project_management_dashboard.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "quantumberg_project_management_dashboard.install.before_install"
# after_install = "quantumberg_project_management_dashboard.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "quantumberg_project_management_dashboard.uninstall.before_uninstall"
# after_uninstall = "quantumberg_project_management_dashboard.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "quantumberg_project_management_dashboard.utils.before_app_install"
# after_app_install = "quantumberg_project_management_dashboard.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "quantumberg_project_management_dashboard.utils.before_app_uninstall"
# after_app_uninstall = "quantumberg_project_management_dashboard.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "quantumberg_project_management_dashboard.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "quantumberg_project_management_dashboard.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["quantumberg_project_management_dashboard.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"quantumberg_project_management_dashboard.tasks.all"
# 	],
# 	"daily": [
# 		"quantumberg_project_management_dashboard.tasks.daily"
# 	],
# 	"hourly": [
# 		"quantumberg_project_management_dashboard.tasks.hourly"
# 	],
# 	"weekly": [
# 		"quantumberg_project_management_dashboard.tasks.weekly"
# 	],
# 	"monthly": [
# 		"quantumberg_project_management_dashboard.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "quantumberg_project_management_dashboard.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "quantumberg_project_management_dashboard.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "quantumberg_project_management_dashboard.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "quantumberg_project_management_dashboard.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["quantumberg_project_management_dashboard.utils.before_request"]
# after_request = ["quantumberg_project_management_dashboard.utils.after_request"]

# Job Events
# ----------
# before_job = ["quantumberg_project_management_dashboard.utils.before_job"]
# after_job = ["quantumberg_project_management_dashboard.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"quantumberg_project_management_dashboard.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

