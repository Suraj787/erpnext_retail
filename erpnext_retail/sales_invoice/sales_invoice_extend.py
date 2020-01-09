import frappe
import pdb


def calculate_correct_taxes(doc, method):
    pdb.set_trace()
    sales_items = doc.items
    company = doc.company

    for sales_item in sales_items:
        item = sales_item.item_code
        item_group = sales_item.item_group
        rate = sales_item.rate

        # Trying for Specific Item
        corrected_tax = correct_tax_template('Selling', 'Item', company, rate, item)
        if corrected_tax:
            sales_item.item_tax_template = corrected_tax
            continue

        # Trying for ITem group
        corrected_tax = correct_tax_template('Selling', 'Item Group', company, rate, None, item_group)
        if corrected_tax:
            sales_item.item_tax_template = corrected_tax
            continue

        # Trying for All
        corrected_tax = correct_tax_template('Selling', 'All', company)
        if corrected_tax:
            sales_item.item_tax_template = corrected_tax


def correct_tax_template(transaction_type, for_item, company, rate, item=None, item_group=None):
    price_wise_tax = None
    filter = {
        'transaction': transaction_type,
        'company': company,
        'for': for_item
    }

    if for_item == 'Item':
        if not item:
            return False

        filter['item'] = item

    if for_item == 'Item Group':
        if not item_group:
            return False

        filter['item_group'] = item_group

    price_wise_tax = frappe.get_all('Price Based Tax Category Selection', filters=filter)

    if not price_wise_tax or len(price_wise_tax) > 1:
        return False
    else:
        return get_tax_template(price_wise_tax[0]['name'], rate)


def get_tax_template(price_wise_tax, rate):
    to_return = None

    price_wise_tax_object = frappe.get_doc('Price Based Tax Category Selection', price_wise_tax)

    if not price_wise_tax:
        return None

    price_rules = price_wise_tax_object.rule

    for price_rule in price_rules:
        if(rate >= float(price_rule.from_price) and rate <= float(price_rule.to_price)):
            to_return = price_rule.tax_template
            break

    return to_return
