from __future__ import unicode_literals

import frappe

def get_context(context):
    # do your magic here
    pass


@frappe.whitelist()		
def get_customer(customer):
    address = frappe.db.sql("select a.address_line1,a.address_line2,a.city,a.state,a.pincode from `tabAddress` a LEFT JOIN `tabDynamic Link` dl on dl.parent = a.name LEFT JOIN `tabCustomer` c on dl.link_name = c.name where dl.link_name=%s", customer)
    return address

@frappe.whitelist()		
def create_new_address(customer,new_address,city,address_title,state,pin_code):
    if customer:
        address = frappe.new_doc('Address')
        address.address_title = address_title + customer
        address.address_line1 = new_address
        address.city = city
        address.state = state
        address.pin_code = pin_code
        address.append("links",{
                            'link_doctype':"Customer",
                            'link_name':customer,
                            'link_title':customer                                                       
                        })
            
        address.insert()
        address.save()
        frappe.msgprint("Add New Address Create")
    else:
        frappe.msgprint("Customer Not Null")
        