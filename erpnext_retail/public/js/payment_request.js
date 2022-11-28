frappe.ui.form.on('Payment Request', {
    status: function(frm) {
		if(frm.doc.status == "Paid"){
		frappe.call({
        method: 'erpnext_retail.erpnext_retail.custom_script.payment_request.auto_sales_invoice',
        args: {
            so : cur_frm.doc.reference_name
        }
        });
		}
	}
});
