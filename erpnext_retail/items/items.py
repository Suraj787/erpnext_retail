import frappe
from erpnext.controllers.item_variant import enqueue_multiple_variant_creation
import json
from six import string_types


def chunk(l, n):
        for i in range(0, len(l), n):
                yield l[i:i+n]

def add_item_barcode(item_code):
    item = frappe.get_doc('Item', item_code)
    item_code_split = item.name.split("STOITEM")

    if(len(item_code_split) != 2):
        return

    barcode_digit = item_code_split[1]
    barcode_exist = False

    for barcode in item.barcodes:
        if barcode_digit == barcode.barcode:
            barcode_exist = True
            break

    if not barcode_exist:
        barcode = item.append('barcodes', {})
        barcode.barcode = barcode_digit
        barcode.barcode_type = ""
        barcode.barcode_print = barcode_digit
        barcode.save()
        item.save()

        #frappe.db.commit()


@frappe.whitelist()
def add_items(doc, item_attribute, company, item_price_array, item_name,
              item_group, article, brand, hsn, purchase_invoice_doc):

        if not company:
                frappe.msgprint('Company Not Provided')
                return

        if not item_attribute:
                frappe.msgprint('Item Attribute Not Provided')
                return

        item_attribute_doc = frappe.get_doc('Item Attribute', item_attribute)

        if not item_attribute_doc:
                frappe.msgprint('Item Attribute Not Present')
                return

        is_numeric = False
        if item_attribute_doc.numeric_values == 1:
                is_numeric = True

        item_attribute_values = []
        if is_numeric:
                from_range = int(item_attribute_doc.from_range)
                to_range = int(item_attribute_doc.to_range)
                increment = int(item_attribute_doc.increment)

                for attribute_value in range(from_range, to_range + 1, increment):
                        item_attribute_values.append(attribute_value)
        else:
                for item_attribute_value in item_attribute_doc.item_attribute_values:
                        item_attribute_values.append(item_attribute_value.attribute_value)

        item_price_array_final = {}
        attribute_array = []
        error = False
        item_price_array = json.loads(item_price_array)
        for item_price in item_price_array:
                qty = int(item_price['qty'])
                if qty == 0:
                        continue

                attr = item_price['attr']
                if is_numeric:
                        attr = int(attr)

                if not (attr in item_attribute_values):
                        error = True
                        frappe.msgprint("%s attribute value is incorrect" % (attr))
                        continue
                else:
                        attribute_array.append(attr)
                        item_price_array_final[attr] = item_price

        if error:
                frappe.msgprint('Please Check attribute values and try again')
                return

        # Crreate New Template Item
        template_attributes = []

        if(is_numeric):
                template_attributes.append({
                        "attribute": item_attribute,
                        "from_range": from_range,
                        "to_range": to_range,
                        "increment": increment,
                        "numeric_values": 1
                })
        else:
                template_attributes.append({
                        "attribute": item_attribute
                })

        try:
                template = frappe.get_doc({
                        "doctype": 'Item',
                        "item_name": item_name,
                        "item_group": item_group,
                        "article": article,
                        "brand": brand,
                        "gst_hsn_code": hsn,
                        "has_variants": 1,
                        "variant_based_on": 'Item Attribute',
                        "attributes": template_attributes
                })

                template.insert()

                variant_item_cunks = list(chunk(attribute_array, 9))
                for variant_item_array in variant_item_cunks:
                        count = enqueue_multiple_variant_creation(
                            template.name, json.dumps({item_attribute: variant_item_array}))
                        if count != len(variant_item_array):
                                raise Exception('Some Error')

                if is_numeric:
                        attribute_array = list(map(str, attribute_array))

                items = frappe.get_all(
                    'Item',
                    filters=[['Item Variant Attribute', 'variant_of', '=', template.name],
                             ['Item Variant Attribute', 'attribute', '=', item_attribute],
                             ['Item Variant Attribute', 'attribute_value', 'in', attribute_array]],)

                if isinstance(doc, string_types):
                        doc = frappe.get_doc(json.loads(doc))

                if doc:
                        for item in items:
                                add_item_barcode(item.name)
                                item_doc = frappe.get_doc('Item', item.name)

                                attr = ''
                                for attribute in item_doc.attributes:
                                        if attribute.attribute == item_attribute:
                                                attr = attribute.attribute_value
                                                break

                                if attr == '':
                                        raise Exception('Error')

                                if is_numeric:
                                        attr = int(attr)

                                item_details = item_price_array_final[attr]
                                pi_item = doc.append("items")
                                pi_item.item_name = item_doc.item_name
                                pi_item.item_group = item_doc.item_group
                                pi_item.item_code = item_doc.name
                                pi_item.uom = item_doc.stock_uom
                                pi_item.received_qty = item_details['qty']
                                pi_item.qty = item_details['qty']
                                pi_item.rate = item_details['rate']
                                pi_item_price = frappe.get_doc({
                                        "doctype": "Item Price",
                                        "item_code": item_doc.name,
                                        "price_list": "Standard Selling",
                                        "price_list_rate": item_details['mrp']
                                })

                                pi_item_price.insert()

                frappe.db.commit()
                return doc
        except BaseException:
                frappe.db.rollback()
                return False
