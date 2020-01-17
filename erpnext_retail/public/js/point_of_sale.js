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
            () => this.page.set_title(__(this.frm.doc.company + " Point of Sale"))
        ]);
    }
}

erpnext.pos.PointOfSale = PointOfSaleNew

class PaymentNew extends Payment{
    get_fields() {
        const me = this;

        let fields = this.frm.doc.payments.map((p) => {
            return {
                fieldtype: "Currency",
                label: __(p.mode_of_payment),
                options: me.frm.doc.currency,
                fieldname: p.mode_of_payment,
                default: p.amount,
                onchange: () => {
                    const value = this.dialog.get_value(this.fieldname) || 0;
                    me.update_payment_value(this.fieldname, value);
                }
            };
        });

        fields = fields.concat([
            {
                fieldtype: "Column Break",
            },
            {
                fieldtype: "HTML",
                fieldname: "numpad"
            },
            {
                fieldtype: "Section Break",
                depends_on: "eval: this.invoice_frm.doc.loyalty_program"
            },
            {
                fieldtype: "Check",
                label: "Redeem Loyalty Points",
                fieldname: "redeem_loyalty_points",
                onchange: () => {
                    me.update_cur_frm_value("redeem_loyalty_points", () => {
                        frappe.flags.redeem_loyalty_points = false;
                        me.update_loyalty_points();
                    });
                }
            },
            {
                fieldtype: "Column Break",
            },
            {
                fieldtype: "Int",
                fieldname: "loyalty_points",
                label: __("Loyalty Points"),
                depends_on: "redeem_loyalty_points",
                onchange: () => {
                    me.update_cur_frm_value("loyalty_points", () => {
                        frappe.flags.loyalty_points = false;
                        me.update_loyalty_points();
                    });
                }
            },
            {
                fieldtype: "Currency",
                label: __("Loyalty Amount"),
                fieldname: "loyalty_amount",
                options: me.frm.doc.currency,
                read_only: 1,
                depends_on: "redeem_loyalty_points"
            },
            {
                fieldtype: "Section Break",
            },
            {
                fieldtype: "Currency",
                label: __("Write off Amount"),
                options: me.frm.doc.currency,
                fieldname: "write_off_amount",
                default: me.frm.doc.write_off_amount,
                onchange: () => {
                    me.update_cur_frm_value("write_off_amount", () => {
                        frappe.flags.change_amount = false;
                        me.update_change_amount();
                    });
                }
            },
            {
                fieldtype: "Column Break",
            },
            {
                fieldtype: "Currency",
                label: __("Change Amount"),
                options: me.frm.doc.currency,
                fieldname: "change_amount",
                default: me.frm.doc.change_amount,
                onchange: () => {
                    me.update_cur_frm_value("change_amount", () => {
                        frappe.flags.write_off_amount = false;
                        me.update_write_off_amount();
                    });
                }
            },
            {
                fieldtype: "Section Break",
            },
            {
                fieldtype: "Currency",
                label: __("Paid Amounts"),
                options: me.frm.doc.currency,
                fieldname: "paid_amount",
                default: me.frm.doc.paid_amount,
                read_only: 1
            },
            {
                fieldtype: "Column Break",
            },
            {
                fieldtype: "Currency",
                label: __("Outstanding Amount"),
                options: me.frm.doc.currency,
                fieldname: "outstanding_amount",
                default: me.frm.doc.outstanding_amount,
                read_only: 1
            },
            {
                fieldtype: "Section Break",
            },
            {
                fieldtype: "Link",
                options: "Sales Person",
                fieldname: "sales_person",
                label: __("Sales Person"),
                onchange: () => {
                    me.update_commission_rate();
                }
            },
            {
                fieldtype: "Column Break",
            },
            {
                fieldtype: "Float",
                label: __("Commission"),
                fieldname: "sales_commission",
                read_only: 1
            }
        ]);

        return fields;

    }

    update_commission_rate(){
        const sales_person = this.dialog.get_value("sales_person");
        var self = this;
        if(sales_person){
            frappe.db.get_doc("Sales Person", sales_person)
                .then(function(sales_person_object){
                    if(sales_person_object){
                        self.dialog.set_value("sales_commission", sales_person_object.commission_rate);
                    }
                }).catch(function(error){
                    frappe.msgprint(error)
                });
        }
    }

    update_sales_man(){
        this.frm.doc.sales_team = [];
        this.frm.refresh_field("sales_team");

        const sales_person = this.dialog.get_value("sales_person");
        const commission_rate = this.dialog.get_value("sales_commission");
        if(sales_person){
            var child_table = frappe.model.add_child(this.frm.doc, "Sales Team", "sales_team");
            frappe.model.set_value(child_table.doctype, child_table.name, "sales_person", sales_person);
            frappe.model.set_value(child_table.doctype, child_table.name, "allocated_percentage", 100);
            frappe.model.set_value(child_table.doctype, child_table.name, "commission_rate", commission_rate);
            this.frm.refresh_field("sales_team");
            this.dialog.set_value("sales_commission", "");
            this.dialog.set_value("sales_person", "");
            this.dialog.refresh();
        }
    }

    set_primary_action() {
        var me = this;

        this.dialog.set_primary_action(__("Submit"), function() {
            me.dialog.hide();
            me.update_sales_man();
            me.events.submit_form();
        });
    }
}

Payment = PaymentNew;
