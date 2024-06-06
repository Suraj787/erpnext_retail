# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "erpnext_retail"
app_title = "Erpnext Retail"
app_publisher = "Techlift"
app_description = "ERPNext Retail Customization"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "palash@techlift.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_retail/css/erpnext_retail.css"
app_include_js = "/assets/erpnext_retail/js/erpnext_retail.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_retail/css/erpnext_retail.css"
# web_include_js = "/assets/erpnext_retail/js/erpnext_retail.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}
page_js = {"point-of-sale": "public/js/point_of_sale.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
        "Purchase Invoice": ["public/js/purchase_invoice.js", "public/js/tax_correction.js"],
        "Sales Invoice": ["public/js/tax_correction.js", "public/js/sales_invoice.js"],
        "Sales Order": ["public/js/tax_correction.js", "public/js/sales_order.js"]
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "erpnext_retail.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "erpnext_retail.install.before_install"
# after_install = "erpnext_retail.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_retail.notifications.get_notification_config"

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

doc_events = {
     "Payment Request":{
          "on_change":"erpnext_retail.erpnext_retail.custom_script.payment_request.on_change"
     },
        "Delivery Note":{
          "on_submit":"erpnext_retail.erpnext_retail.custom_script.delivery_note.on_submit"
     },
        "Sales Invoice":{
          "on_submit":"erpnext_retail.erpnext_retail.custom_script.sales_invoice.on_submit"
     },
        "Sales Invoice":{
          "validate":"erpnext_retail.erpnext_retail.custom_script.sales_invoice.validate"
     },
     
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_retail.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_retail.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_retail.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_retail.tasks.weekly"
# 	]
# 	"monthly": [
# 		"erpnext_retail.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "erpnext_retail.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_retail.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_retail.task.get_dashboard_data"
# }

