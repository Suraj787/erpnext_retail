frappe.ui.form.on('Sales Invoice', {
    async validate(frm) {
        console.log("Ccccc")
        await correct_taxes(frm, "Selling", false)
    }
})

frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        console.log("Ddddd")
        await correct_taxes(frm, "Selling", false)
    }
})

frappe.ui.form.on('Purchase Invoice', {
    async before_save(frm) {
        var place_of_supply = frm.doc.place_of_supply
        var supplier_gstin = frm.doc.supplier_gstin
        var bypass_gst_comparition = false
        var outstate = false

        if ((!place_of_supply) || (!supplier_gstin)) {
            bypass_gst_comparition = true
        }

        if (!bypass_gst_comparition) {
            var supplier_gst_location = supplier_gstin.substr(0, 2)
            var our_gst_location = place_of_supply.substr(0, 2)

            if (supplier_gst_location != our_gst_location) {
                outstate = true
            }
        }
        await correct_taxes(frm, "Buying", outstate)
    }
})

var price_wise_tax_cache = {}

async function get_tax_template(price_wise_tax, rate, outstate) {
    let to_return = false;

    let price_wise_tax_object;
    if (!(price_wise_tax in price_wise_tax_cache)) {
        price_wise_tax_object = await frappe.db.get_doc('Price Based Tax Category Selection', price_wise_tax);
        price_wise_tax_cache[price_wise_tax.name] = price_wise_tax_object
    } else {
        price_wise_tax_object = price_wise_tax_cache[price_wise_tax]
    }

    if (!price_wise_tax_object) {
        return false;
    }

    let price_rules = price_wise_tax_object.rule

    for (let price_rule of price_rules) {
        if ((outstate && price_rule.place != "Outstate") || (!outstate && price_rule.place != "Instate")) {
            continue
        }

        if (rate >= price_rule.from_price && rate <= price_rule.to_price) {
            to_return = price_rule.tax_template
            break;
        }
    }

    return to_return
}

async function correct_taxes(frm, transaction_type, outstate = false) {
    console.log("here")
    frappe.dom.freeze()
    let sales_items = frm.doc.items
    let company = frm.doc.company

    var price_wise_taxes = await frappe.db.get_list('Price Based Tax Category Selection', {
        fields: ["name", "for_item", "item", "item_group"],
        limit: 1000,
        filters: { "company": frm.doc.company, "transaction": transaction_type }
    })

    // console.log(price_wise_taxes, "price_wise_taxes======")
    var price_wise_tax_mapping = {}

    for (var price_wise_tax of price_wise_taxes) {
        var for_item = price_wise_tax.for_item
        if (!(for_item in price_wise_tax_mapping)) {
            if (for_item == "All") {
                price_wise_tax_mapping[for_item] = price_wise_tax.name
            } else {
                price_wise_tax_mapping[for_item] = {}
                if (for_item == "Item") {
                    price_wise_tax_mapping[for_item][price_wise_tax.item] = price_wise_tax.name
                }
                if (for_item == "Item Group") {
                    price_wise_tax_mapping[for_item][price_wise_tax.item_group] = price_wise_tax.name
                }
            }
        } else {
            if (for_item == "Item") {
                price_wise_tax_mapping[for_item][price_wise_tax.item] = price_wise_tax.name
            }
            if (for_item == "Item Group") {
                price_wise_tax_mapping[for_item][price_wise_tax.item_group] = price_wise_tax.name
            }
        }
    }

    var additional_discount_percentage = frm.doc.additional_discount_percentage
    var disscount_apply_on = frm.doc.apply_discount_on
    var discont_amount = frm.doc.discount_amount

    for (let sales_item of sales_items) {
        var item = sales_item.item_code
        var item_group = sales_item.item_group
        var rate = sales_item.rate
        var tax_template

        if (discont_amount) {
            additional_discount_percentage = (discont_amount * 100) / frm.doc.total
        }

        if (additional_discount_percentage) {
            rate = rate - rate * (additional_discount_percentage / 100)
        }

        //Check for Item
        if ("Item" in price_wise_tax_mapping && item in price_wise_tax_mapping["Item"]) {
            tax_template = await get_tax_template(price_wise_tax_mapping["Item"][item], rate, outstate);
        }
        else if ("Item Group" in price_wise_tax_mapping && item_group in price_wise_tax_mapping["Item Group"]) {
            tax_template = await get_tax_template(price_wise_tax_mapping["Item Group"][item_group], rate, outstate);
        }
        else if ("All" in price_wise_tax_mapping) {
            tax_template = await get_tax_template(price_wise_tax_mapping["All"], rate, outstate);
        }

        if (tax_template) {
            console.log(tax_template,"on-----")
            await frappe.model.set_value(sales_item.doctype, sales_item.name, "item_tax_template", tax_template)
            frm.refresh_field("items")
        }
    }
    frm.refresh_fields()
    frappe.dom.unfreeze()
}

async function correct_tax_template(transaction_type, for_item, company, rate, item = null, item_group = null) {
    var price_wise_tax = null;
    var filter = {
        'transaction': transaction_type,
        'company': company,
        'for': for_item
    };

    if (for_item == 'Item') {
        if (!item) {
            return false;
        }
        filter['item'] = item
    }

    if (for_item == 'Item Group') {
        if (!item_group) {
            return false;
        }
        filter['item_group'] = item_group
    }

    var price_wise_tax = await frappe.db.get_list('Price Based Tax Category Selection', { filters: filter })

    if (!price_wise_tax || price_wise_tax.length == 0 || price_wise_tax.length > 1) {
        return false;
    } else {
        return await get_tax_template(price_wise_tax[0].name, rate);
    }
}

