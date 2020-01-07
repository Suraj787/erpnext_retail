class PointOfSaleNew extends erpnext.pos.PointOfSale{
	make() {
		return frappe.run_serially([
			() => frappe.dom.freeze(),
			() => {
				this.prepare_dom();
				this.prepare_menu();
				this.set_online_status();
			},
			() => this.make_new_invoice(),
			() => {
				if(!this.frm.doc.company) {
					this.setup_company()
						.then((company) => {
							this.frm.doc.company = company;
							this.get_pos_profile();
						});
				}
			},
			() => {
				frappe.dom.unfreeze();
			},
			() => this.page.set_title(__(this.frm.doc.company + ' Point of Sale'))
		]);
	}
}

erpnext.pos.PointOfSale = PointOfSaleNew
