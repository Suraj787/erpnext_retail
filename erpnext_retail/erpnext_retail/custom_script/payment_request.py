import frappe

def on_submit(doc,method):
    frappe.msgprint(f"submit")
    if doc.payment_url and doc.reference_doctype == "Sales Invoice" and doc.reference_name:
        frappe.msgprint(f"doc.payment_url {doc.payment_url}")
        # payment_request_url =frappe.db.get_value("Payment Request", {'name': pr_doc.name}, "payment_url")
        frappe.db.sql("""update `tabSales Invoice` set payment_request_url = '{0}'
            where name = '{1}'""".format(doc.payment_url,doc.reference_name))
        frappe.db.commit()

def on_change(doc,method):
    try:
        if doc.status == "Paid":
            sales_order = frappe.get_doc("Sales Order",doc.reference_name)
            ref_name=frappe.db.sql(f""" select p.idx,p.reference_doctype,a.name,a.remarks,p.total_amount,p.allocated_amount from `tabPayment Entry` as a inner join `tabPayment Entry Reference` as p on p.parent=a.name where p.reference_name='{doc.reference_name}' and p.idx<=1""",as_dict=1)
            for r in ref_name:
                if str(r.idx) == "1" and str(r.reference_doctype) == "Sales Order":   
                    si = frappe.new_doc("Sales Invoice")
                    si.customer = sales_order.customer
                    si.posting_date = sales_order.transaction_date
                    si.status = "Paid"
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
                    
                    for ref in ref_name:
                        si.append("advances",{
                                'reference_type':"Payment Entry",
                                'reference_name':str(ref.name),
                                'remarks':str(ref.remarks),
                                'advance_amount':str(ref.total_amount),
                                'allocated_amount':str(ref.allocated_amount),                           
                            })    
                        
                        
                    si.insert(ignore_permissions=True)
                    si.submit() 
                    frappe.msgprint("Create Sales Invoice")
    except Exception as e:
        frappe.log_error(
			title=("Error while processing payment request for {0}").format(doc.name),
			message=frappe.get_traceback(),
		)
