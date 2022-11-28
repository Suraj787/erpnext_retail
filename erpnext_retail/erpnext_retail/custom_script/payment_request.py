import frappe

def on_submit(doc,method):
    frappe.msgprint(f"submit")
    if doc.payment_url and doc.reference_doctype == "Sales Invoice" and doc.reference_name:
        frappe.msgprint(f"doc.payment_url {doc.payment_url}")
        # payment_request_url =frappe.db.get_value("Payment Request", {'name': pr_doc.name}, "payment_url")
        frappe.db.sql("""update `tabSales Invoice` set payment_request_url = '{0}'
            where name = '{1}'""".format(doc.payment_url,doc.reference_name))
        frappe.db.commit()
 
def on_update_after_submit(doc,method):
    if doc.status == "Paid":
        sales_order = frappe.get_doc("Sales Order",doc.reference_name)
        si = frappe.new_doc("Sales Invoice")
        si.customer = sales_order.customer
        si.posting_date = sales_order.transaction_date
        for i in sales_order.items:
            
            si.append("items",{
                    'item_code':i.item_code,
                    'item_name':i.item_name,
                    'description':i.description,
                    'uom':i.uom,
                    'qty':i.qty,
                    'conversion_factor':"1",
                    'warehouse':i.warehouse,
                    'rate':i.rate,
                    'amount':i.amount

                                                    
                    })
        si.insert() 
        si.submit() 
        frappe.msgprint("Create Sales Invoice")
