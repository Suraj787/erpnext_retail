import frappe
import json
from frappe import _
from frappe.utils import getdate, today,flt

@frappe.whitelist()
def make_payment_request(doc):
    # frappe.log_error("test")
    doc = json.loads(doc)
    if not check_duplicate_payment_request(doc):
        gateway_account = frappe.db.get_value("Payment Gateway Account", {'is_default':1},
            ["name", "payment_gateway", "payment_account", "message"], as_dict=1)
        pr_doc = frappe.new_doc("Payment Request")
        pr_doc.payment_request_type = "Inward"
        pr_doc.transaction_date = getdate(today())
        pr_doc.party_type = "Customer"
        pr_doc.party = doc.get("customer")
        pr_doc.reference_doctype = "Sales Order"
        pr_doc.reference_name = doc.get('name')
        pr_doc.currency= doc.get('currency')
        pr_doc.contact_mobile= doc.get('contact_phone')
        pr_doc.grand_total = doc.get('base_rounded_total')
        pr_doc.payment_gateway_account = gateway_account.get("name")
        pr_doc.payment_gateway = gateway_account.get("payment_gateway")
        pr_doc.payment_account = gateway_account.get("payment_account")
        pr_doc.payment_channel = gateway_account.get("payment_channel")
        pr_doc.email_to = get_email_id(doc)
        pr_doc.subject = _("Payment Request for {0}").format(doc.get('name'))
        pr_doc.message = gateway_account.get("message") 
        pr_doc.save()
        pr_doc.submit()

        return pr_doc.name
    else:
        frappe.msgprint("Payment Request already exist.")

def check_duplicate_payment_request(doc):
    return  frappe.db.get_all("Payment Request", filters={
            'party_type' : "Customer",
            'party' : doc.get("customer"),
            'grand_total' : get_base_rounded_total(doc),
            'reference_doctype' : "Sales Order",
            'reference_name':doc.get('name'),
            'docstatus':1,
            'name': ['!=', doc.get('name')]
        }, limit=1)

def get_email_id(doc):
    if doc.get('contact_email'):
        return doc.get('contact_email')
    elif doc.get('contact_person'):
        email = frappe.db.get_value("Contact", {'name':doc.get('contact_person')}, 'email_id')
        if email:
            return email
    else:
        return doc.get('owner')

def get_base_rounded_total(doc):
    if doc.get('party_account_currency') == doc.get('currency'):
        grand_total = flt(doc.get('outstanding_amount'))
    else:
        grand_total = flt(doc.get('outstanding_amount')) / doc.get('conversion_rate')
    return grand_total
