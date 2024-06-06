import frappe
from frappe import _
from frappe.utils import getdate, today, flt

def on_submit(doc, method):
    frappe.msgprint("Submit")
    if doc.payment_url and doc.reference_doctype == "Sales Invoice" and doc.reference_name:
        frappe.msgprint(f"doc.payment_url {doc.payment_url}")
        frappe.db.sql("""UPDATE `tabSales Invoice` SET payment_request_url = '{0}'
                         WHERE name = '{1}'""".format(doc.payment_url, doc.reference_name))
        frappe.db.commit()

def on_change(doc, method):
    try:
        if doc.status in ["Paid", "Partially Paid"]:
            sales_order = frappe.get_doc("Sales Order", doc.reference_name, ignore_permissions=True)
            payment_entries = frappe.db.get_list("Payment Entry Reference", filters={"reference_name": doc.reference_name}, fields=["parent", "total_amount", "allocated_amount", "exchange_rate"], ignore_permissions=True)
            payment_entries = [frappe.get_doc("Payment Entry", pe["parent"], ignore_permissions=True) for pe in payment_entries]

            si = frappe.new_doc("Sales Invoice")
            si.customer = sales_order.customer
            si.posting_date = sales_order.transaction_date
            si.due_date = getdate(today())
            si.place_of_supply = sales_order.place_of_supply or None

            for item in sales_order.items:
                si.append("items", {
                    'item_code': item.item_code,
                    'item_name': item.item_name,
                    'description': item.description,
                    'uom': item.uom,
                    'qty': item.qty,
                    'conversion_factor': "1",
                    'warehouse': item.warehouse,
                    'rate': item.rate,
                    'amount': item.amount,
                    "sales_order": item.parent
                })

            if sales_order.taxes_and_charges:
                for tax in sales_order.taxes:
                    si.append("taxes", tax.as_dict())

            si.insert(ignore_permissions=True)

            for payment_entry in payment_entries:
                payment_entry.reload()  # Reload to get the latest version
                for ref in payment_entry.references:
                    try:
                        ref_exchange_rate_val = float(ref.exchange_rate) if ref.exchange_rate is not None else 0.0
                        advance_amount_val = float(ref.total_amount) if ref.total_amount is not None else 0.0
                        allocated_amount_val = float(ref.allocated_amount) if ref.allocated_amount is not None else 0.0
                    except ValueError:
                        frappe.log_error("Error converting types for Payment Entry Advances", "Type Conversion Error")
                        continue  # Optionally skip this entry or handle it differently

                    #si.append("advances", {
                    #    'reference_type': "Payment Entry",
                    #    'reference_name': str(payment_entry.name),
                    #    'remarks': str(payment_entry.remarks) or 'No remarks provided',
                    #    'ref_exchange_rate': ref_exchange_rate_val,
                    #    'advance_amount': advance_amount_val,
                    #    'allocated_amount': allocated_amount_val,
                    #})
            si.set_advances()
            si.submit()
            frappe.db.set_value("Sales Order", sales_order.name, "per_billed", 100)
            frappe.db.set_value("Sales Order", sales_order.name, "status", "To Deliver")
            frappe.db.commit()
            frappe.msgprint("Created Sales Invoice")

    except Exception as e:
        frappe.log_error(title=_("Error while processing payment request for {0}").format(doc.name),
                         message=frappe.get_traceback())

def get_advance_entries(self, include_unallocated=True):
    party_account = self.debit_to if self.doctype == "Sales Invoice" else self.credit_to
    party_type = "Customer" if self.doctype == "Sales Invoice" else "Supplier"
    party = self.customer if self.doctype == "Sales Invoice" else self.supplier
    amount_field = "credit_in_account_currency" if self.doctype == "Sales Invoice" else "debit_in_account_currency"
    order_field = "sales_order" if self.doctype == "Sales Invoice" else "purchase_order"
    order_doctype = "Sales Order" if self.doctype == "Sales Invoice" else "Purchase Order"

    order_list = list(set(d.get(order_field) for d in self.get("items") if d.get(order_field)))

    journal_entries = get_advance_journal_entries(
        party_type, party, party_account, amount_field, order_doctype, order_list, include_unallocated
    )

    payment_entries = get_advance_payment_entries(
        party_type, party, party_account, order_doctype, order_list, include_unallocated
    )

    return journal_entries + payment_entries

