import frappe
import json
from frappe import _
from frappe.utils import getdate, today,flt

def get_tax_template(price_wise_tax, rate, outstate):
    to_return = False
    price_wise_tax_cache = {}
    
    price_wise_tax_object = None
    if price_wise_tax not in price_wise_tax_cache:
        price_wise_tax_object = frappe.get_doc('Price Based Tax Category Selection', price_wise_tax)
        price_wise_tax_cache[price_wise_tax] = price_wise_tax_object
    else:
        price_wise_tax_object = price_wise_tax_cache[price_wise_tax]

    if not price_wise_tax_object:
        return False
   
    price_rules = price_wise_tax_object.rule

    for price_rule in price_rules:
        if (outstate and price_rule.place != "Outstate") or (not outstate and price_rule.place != "Instate"):
            continue

        if rate >= float(price_rule.from_price) and rate <= float(price_rule.to_price):
            to_return = price_rule.tax_template
            break

    return to_return


def get_item_tax_template(item,invoice_doc):
    
    item_obj = frappe._dict(item.as_dict())
       
    company = invoice_doc.company
    price_wise_taxes = frappe.db.get_all('Price Based Tax Category Selection', 
        {"company": "Kothari Collections", "transaction": "Selling"},
        ["name", "for_item", "item", "item_group"],limit=1000)

    price_wise_tax_mapping = {}

    for price_wise_tax in price_wise_taxes:
        for_item = price_wise_tax['for_item']
        if for_item not in price_wise_tax_mapping:
            if for_item == "All":
                price_wise_tax_mapping[for_item] = price_wise_tax['name']
            else:
                price_wise_tax_mapping[for_item] = {}
                if for_item == "Item":
                    price_wise_tax_mapping[for_item][price_wise_tax['item']] = price_wise_tax['name']
                if for_item == "Item Group":
                    price_wise_tax_mapping[for_item][price_wise_tax['item_group']] = price_wise_tax['name']
        else:
            if for_item == "Item":
                price_wise_tax_mapping[for_item][price_wise_tax['item']] = price_wise_tax['name']
            if for_item == "Item Group":
                price_wise_tax_mapping[for_item][price_wise_tax['item_group']] = price_wise_tax['name']

    additional_discount_percentage = invoice_doc.additional_discount_percentage
    disscount_apply_on = invoice_doc.apply_discount_on
    discont_amount = invoice_doc.discount_amount

    item = item_obj.item_code
    item_group = item_obj.item_group
    rate = item_obj.rate
    tax_template = None

    if discont_amount:
        additional_discount_percentage = (discont_amount * 100) / invoice_doc.total

    if additional_discount_percentage:
        rate = rate - rate * (additional_discount_percentage / 100)

    # Check for Item
    outstate = False
    if "Item" in price_wise_tax_mapping and item in price_wise_tax_mapping["Item"]:
        tax_template =  get_tax_template(price_wise_tax_mapping["Item"][item], rate, outstate)
    elif "Item Group" in price_wise_tax_mapping and item_group in price_wise_tax_mapping["Item Group"]:
        tax_template =  get_tax_template(price_wise_tax_mapping["Item Group"][item_group], rate, outstate)
    elif "All" in price_wise_tax_mapping:
        tax_template =  get_tax_template(price_wise_tax_mapping["All"], rate, outstate)

    if tax_template:
        return tax_template

    return None


def on_submit(doc, method):
    doc.due_date = getdate(today())
    if not doc.is_pos:
        for item in doc.items:
            if not item.item_tax_template:
                item.item_tax_template = get_item_tax_template(item,doc)

def validate(doc, method):
    doc.due_date = getdate(today())



@frappe.whitelist()
def make_payment_request(doc):
    doc = json.loads(doc)
    if not check_duplicate_payment_request(doc):
        gateway_account = frappe.db.get_value("Payment Gateway Account", {'is_default':1},
            ["name", "payment_gateway", "payment_account", "message"], as_dict=1)
        pr_doc = frappe.new_doc("Payment Request")
        pr_doc.payment_request_type = "Inward"
        pr_doc.transaction_date = getdate(today())
        pr_doc.party_type = "Customer"
        pr_doc.party = doc.get("customer")
        pr_doc.customer_name = frappe.db.get_value("Customer",doc.get("customer"),"customer_name")
        pr_doc.reference_doctype = "Sales Invoice"
        pr_doc.reference_name = doc.get('name')
        pr_doc.currency= doc.get('currency')
        pr_doc.grand_total = get_grand_total(doc)
        pr_doc.payment_gateway_account = gateway_account.get("name")
        pr_doc.payment_gateway = gateway_account.get("payment_gateway")
        pr_doc.payment_account = gateway_account.get("payment_account")
        pr_doc.payment_channel = gateway_account.get("payment_channel")
        pr_doc.email_to = get_email_id(doc)
        pr_doc.subject = _("Payment Request for {0}").format(doc.get('name'))
        pr_doc.message = gateway_account.get("message") 
        pr_doc.save()
        pr_doc.submit()
        frappe.msgprint(frappe.db.get_value("Customer",doc.get("customer"),"customer_name"))
        return pr_doc.name
    else:
        frappe.msgprint("Payment Request already exist.")

def check_duplicate_payment_request(doc):
    return  frappe.db.get_all("Payment Request", filters={
            'party_type' : "Customer",
            'party' : doc.get("customer"),
            'grand_total' : get_grand_total(doc),
            'reference_doctype' : "Sales Invoice",
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

def get_grand_total(doc):
    if doc.get('party_account_currency') == doc.get('currency'):
        grand_total = flt(doc.get('outstanding_amount'))
    else:
        grand_total = flt(doc.get('outstanding_amount')) / doc.get('conversion_rate')
    return grand_total
