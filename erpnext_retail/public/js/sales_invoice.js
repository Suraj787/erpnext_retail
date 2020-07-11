frappe.ui.form.on('Sales Invoice', {
    validate(frm){
        correct_taxes(frm)
    }
})

async function get_tax_template(price_wise_tax, rate){
    let to_return = false;

    let price_wise_tax_object = await frappe.db.get_doc('Price Based Tax Category Selection', price_wise_tax);

    if(!price_wise_tax_object){
        return false;
    }

    let price_rules = price_wise_tax_object.rule

    for(let price_rule of price_rules){
        if(rate >= price_rule.from_price && rate <= price_rule.to_price){
            to_return = price_rule.tax_template
            break;
        }
    }

    return to_return
}

async function correct_taxes(frm){
    alert('hi')
    frappe.dom.freeze()
    let sales_items = frm.doc.items
    let company = frm.doc.company

    for(let sales_item of sales_items){
        var item = sales_item.item_code
        var item_group = sales_item.item_group
        var rate = sales_item.rate


        var corrected_tax = await correct_tax_template('Selling', 'Item', company, rate, item)
        if(corrected_tax){
            frappe.model.set_value(sales_item.doctype, sales_item.name, "item_tax_template", corrected_tax)
            continue;
        }


        var corrected_tax = await correct_tax_template('Selling', 'Item Group', company, rate, null, item_group)
        if(corrected_tax){
            frappe.model.set_value(sales_item.doctype, sales_item.name, "item_tax_template", corrected_tax)
            continue;
        }


        var corrected_tax = await correct_tax_template('Selling', 'Item', company, rate)
        if(corrected_tax){
            frappe.model.set_value(sales_item.doctype, sales_item.name, "item_tax_template", corrected_tax)
            continue;
        }
    }
    frappe.dom.unfreeze()
}

async function correct_tax_template(transaction_type, for_item, company, rate, item = null, item_group = null){
    var price_wise_tax = null;
    var filter = {
        'transaction': transaction_type,
        'company': company,
        'for': for_item
    };

    if(for_item == 'Item'){
        if(!item){
            return false;
        }
        filter['item'] = item
    }

    if(for_item == 'Item Group'){
        if(!item_group){
            return false;
        }
        filter['item_group'] = item_group
    }

    var price_wise_tax = await frappe.db.get_list('Price Based Tax Category Selection', {filters:filter})

    if(!price_wise_tax || price_wise_tax.count > 1){
        return false;
    } else {
        return await get_tax_template(price_wise_tax[0].name, rate);
    }
}

