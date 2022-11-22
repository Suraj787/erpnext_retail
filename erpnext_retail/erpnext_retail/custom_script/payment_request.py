import frappe

def on_submit(doc,method):
    frappe.msgprint(f"submit")
    if doc.payment_url and doc.reference_doctype == "Sales Invoice" and doc.reference_name:
        frappe.msgprint(f"doc.payment_url {doc.payment_url}")
        # payment_request_url =frappe.db.get_value("Payment Request", {'name': pr_doc.name}, "payment_url")
        frappe.db.sql("""update `tabSales Invoice` set payment_request_url = '{0}'
            where name = '{1}'""".format(doc.payment_url,doc.reference_name))
        frappe.db.commit()
