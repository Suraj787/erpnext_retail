frappe.ready(function() {
    // bind events here
    frappe.web_form.after_load = () => {

        frappe.web_form.on('customer', () => {
            frappe.call({
                method: 'erpnext_retail.erpnext_retail.web_form.customer_and_shipping_details.customer_and_shipping_details.get_customer',
                args: {
                    customer: frappe.web_form.get_value("customer")
                },
                callback: function(r) {
                    frappe.web_form.set_value("address", r.message[0])
                    frappe.web_form.set_value("second_address", r.message[1])
                    frappe.web_form.set_value("third_address", r.message[2])
                    frappe.web_form.set_value("fourth_address", r.message[3])
                    frappe.web_form.set_value("fifth_address", r.message[4])
                        // console.log(r)
                }
            });

        })

        frappe.web_form.add_button_to_footer("Create Address", "submit", () => {
            frappe.call({
                method: 'erpnext_retail.erpnext_retail.web_form.customer_and_shipping_details.customer_and_shipping_details.create_new_address',
                args: {
                    customer: frappe.web_form.get_value("customer"),
                    new_address: frappe.web_form.get_value("new_address"),
                    city: frappe.web_form.get_value("city"),
                    address_title: frappe.web_form.get_value("address_title"),
                    state: frappe.web_form.get_value("state"),
                    pin_code: frappe.web_form.get_value("pin_code")

                },
                // callback: function(r) {

                //         // console.log(r)
                // }
            });
        })

    };
})