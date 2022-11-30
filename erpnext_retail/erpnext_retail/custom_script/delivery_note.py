import frappe

def on_submit(doc,method):
    for i in doc.items:
        sales_order = i.against_sales_order
   
    td = frappe.new_doc("Tracking Details")
    td.sales_order = sales_order
    td.courier_type = doc.courier_type
    td.shipping_address = doc.shipping_address
    
    td.insert()
    td.save
    frappe.msgprint("Create Tracking Details Successfully")
    
   
    
