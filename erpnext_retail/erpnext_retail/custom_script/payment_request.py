import frappe

def on_submit(doc,method):
    if doc.payment_url and doc.reference_doctype == "Sales Invoice" and doc.reference_name:
        # payment_request_url =frappe.db.get_value("Payment Request", {'name': pr_doc.name}, "payment_url")
        frappe.db.sql("""update `tabSales Invoice` set payment_request_url = '{0}'
            where name = '{1}'""".format(doc.payment_url,doc.reference_name))
        frappe.db.commit()