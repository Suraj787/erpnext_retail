# Copyright (c) 2022, Techlift and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

#class LiveSchedule(Document):
#	pass


@frappe.whitelist()
def liveSchedule_list(doc):
	doc= json.loads(doc)
	live_schd_list=frappe.db.sql(f""" select name from `tabLive Schedule` where schedule_date between 
	"{doc.get("live_from_date")}" and "{doc.get("live_to_date")}" """,as_dict=0)
	frappe.msgprint(live_schd_list)
	return live_schd_list
