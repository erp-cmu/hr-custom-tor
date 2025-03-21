app_name = "hr_custom_tor"
app_title = "Hr Custom Tor"
app_publisher = "IECMU"
app_description = "Custom HRRM for Tor Drink"
app_email = "iecmu@cmu.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "hr_custom_tor",
# 		"logo": "/assets/hr_custom_tor/logo.png",
# 		"title": "Hr Custom Tor",
# 		"route": "/hr_custom_tor",
# 		"has_permission": "hr_custom_tor.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hr_custom_tor/css/hr_custom_tor.css"
# app_include_js = "/assets/hr_custom_tor/js/hr_custom_tor.js"

# include js, css files in header of web template
# web_include_css = "/assets/hr_custom_tor/css/hr_custom_tor.css"
# web_include_js = "/assets/hr_custom_tor/js/hr_custom_tor.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hr_custom_tor/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Leave Application": "public/js/leave_application.js"}
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hr_custom_tor/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hr_custom_tor.utils.jinja_methods",
# 	"filters": "hr_custom_tor.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hr_custom_tor.install.before_install"
# after_install = "hr_custom_tor.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hr_custom_tor.uninstall.before_uninstall"
# after_uninstall = "hr_custom_tor.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hr_custom_tor.utils.before_app_install"
# after_app_install = "hr_custom_tor.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hr_custom_tor.utils.before_app_uninstall"
# after_app_uninstall = "hr_custom_tor.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hr_custom_tor.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Salary Slip": "hr_custom_tor.overrides.custom_salary_slip.CustomSalarySlip",
    "Leave Application": "hr_custom_tor.overrides.custom_leave_application.CustomLeaveApplication",
}

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
# 		"hr_custom_tor.tasks.all"
# 	],
# 	"daily": [
# 		"hr_custom_tor.tasks.daily"
# 	],
# 	"hourly": [
# 		"hr_custom_tor.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hr_custom_tor.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hr_custom_tor.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hr_custom_tor.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hr_custom_tor.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hr_custom_tor.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hr_custom_tor.utils.before_request"]
# after_request = ["hr_custom_tor.utils.after_request"]

# Job Events
# ----------
# before_job = ["hr_custom_tor.utils.before_job"]
# after_job = ["hr_custom_tor.utils.after_job"]

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
# 	"hr_custom_tor.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


fixtures = [
    {"doctype": "Custom Field", "filters": [["module", "=", "hr_custom_tor"]]},
    "Employee",
    "Shift Type",
    {
        "doctype": "Custom Field",
        "filters": [["name", "in", ("Leave Application-custom_hours",)]],
    },
    {
        "doctype": "Property Setter",
        "filters": [["name", "in", ("Leave Application-total_leave_days-precision",)]],
    },
]
