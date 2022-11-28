frappe.ui.form.on('Sales Order', {
	refresh:function(frm){
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__('Payment Request'), function() {
	            frappe.call({
					method: "erpnext_retail.erpnext_retail.custom_script.sales_order.make_payment_request",
					args:{
			          'doc':frm.doc
			        },
			        callback: function(r) {
						if(r.message) {
							frappe.msgprint({
								message: __('Payment Request Created: {0}',
										 [repl('<a href="/app/payment-request/%(name)s">%(name)s</a>', {name:r.message})]
									),
								indicator: 'green'
							})
						}
					}
				});
			})
		}
       
	}
});
	                