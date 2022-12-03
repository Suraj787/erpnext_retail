import frappe
from frappe import _


def on_submit(doc,method):
	frappe.msgprint(f"submit")
	if doc.payment_url and doc.reference_doctype == "Sales Invoice" and doc.reference_name:
		frappe.msgprint(f"doc.payment_url {doc.payment_url}")
		# payment_request_url =frappe.db.get_value("Payment Request", {'name': pr_doc.name}, "payment_url")
		frappe.db.sql("""update `tabSales Invoice` set payment_request_url = '{0}'
			where name = '{1}'""".format(doc.payment_url,doc.reference_name))
		frappe.db.commit()
		
def after_insert(doc,method):
    if doc.party:
        add = frappe.db.sql("select a.address_line1,a.address_line2,a.city,a.state,a.pincode,a.country from `tabAddress` a LEFT JOIN `tabDynamic Link` dl on dl.parent = a.name LEFT JOIN `tabCustomer` c on dl.link_name = c.name where dl.link_name=%s",doc.party)
        add = str(add)
        add=add.replace("(","")
        add=add.replace(")","")
        add=add.replace("'","")
        # frappe.msgprint(str(add))
        customer_address = frappe.new_doc('Customer and Shiping Details')
        customer_address.customer = doc.party
        customer_address.payment_request = doc.name
        customer_address.address = add
        customer_address.insert()
        customer_address.save()
        frappe.msgprint("Customer Address Create")		

def on_change(doc,method):
	try:
		if doc.status == "Paid" or doc.status=="Partially Paid":
			sales_order = frappe.get_doc("Sales Order",doc.reference_name)
			ref_name=frappe.db.sql(f""" select a.name,a.remarks,p.total_amount,p.allocated_amount from `tabPayment Entry` as a inner join `tabPayment Entry Reference` as p on p.parent=a.name where p.reference_name='{doc.reference_name}'""",as_dict=1)
		   
			si = frappe.new_doc("Sales Invoice")
			si.customer = sales_order.customer
			si.posting_date =sales_order.transaction_date
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
						'amount':i.amount  ,
						"sales_order":sales_order.name                                               
						})
			
			si.insert(ignore_permissions=True)
			
		   
			# for ref in ref_name:
			#     si.append("advances",{
			#             'reference_type':"Payment Entry",
			#             'reference_name':str(ref.name),
			#             'remarks':str(ref.remarks),
			#             'advance_amount':str(ref.total_amount),
			#             'allocated_amount':str(ref.allocated_amount),                           
			#         }) 
			si.set_advances()
			# frappe.log_error(si.get("advances"))
			si.submit() 
			frappe.msgprint("Create Sales Invoice")
	except Exception as e:
		frappe.log_error(
						title=_("Error while processing payment request for {0}").format(doc.name),
						message=frappe.get_traceback(),
				)

def get_advance_entries(self, include_unallocated=True):
		if self.doctype == "Sales Invoice":
			party_account = self.debit_to
			party_type = "Customer"
			party = self.customer
			amount_field = "credit_in_account_currency"
			order_field = "sales_order"
			order_doctype = "Sales Order"
		else:
			party_account = self.credit_to
			party_type = "Supplier"
			party = self.supplier
			amount_field = "debit_in_account_currency"
			order_field = "purchase_order"
			order_doctype = "Purchase Order"

		order_list = list(set(d.get(order_field) for d in self.get("items") if d.get(order_field)))

		journal_entries = get_advance_journal_entries(
			party_type, party, party_account, amount_field, order_doctype, order_list, include_unallocated
		)

		payment_entries = get_advance_payment_entries(
			party_type, party, party_account, order_doctype, order_list, include_unallocated
		)

		res = journal_entries + payment_entries

		return res
