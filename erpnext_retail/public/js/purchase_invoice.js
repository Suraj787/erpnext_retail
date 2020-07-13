frappe.ui.keys.add_shortcut({
	shortcut: 'ctrl+i',
	action: function(e) {
		e.preventDefault();
		open_item_helper(cur_frm)
	},
	description: 'Test'
})

function update_item_edit_table(sell_rate, purchase_rate) {
	$('table#items_edit input[data-fieldname^=mrp_rate]').val(sell_rate)
	$('table#items_edit input[data-fieldname^=buying_rate]').val(purchase_rate)
}
function update_prices(d) {
	var purchase_rate = d.fields_dict.rate.get_value()
	var sell_rate = d.fields_dict.sell_rate.get_value()

	update_item_edit_table(sell_rate, purchase_rate)
}

function caluclate_selling_price(d) {
	var purchase_rate = d.fields_dict.rate.get_value()
	var percent = d.fields_dict.percent.get_value()
	if ((purchase_rate <= 0)) {
		return false
	}
	var sell_rate = Number(purchase_rate) + (Number(percent) * Number(purchase_rate)) / 100
	d.set_value('sell_rate', sell_rate)
}

function get_final_item_values(d, company) {
	var item_attribute = d.fields_dict.item_attribute_select.get_value()
	var item_name = d.fields_dict.item_name.get_value()
	var item_group = d.fields_dict.item_group.get_value()
	var article = d.fields_dict.article.get_value()
	var brand = d.fields_dict.brand.get_value()
	var hsn = d.fields_dict.hsn.get_value()

	var items_edit_body = $('#items_edit_body')
	var items_edit_rows = items_edit_body.find('tr')

	var item_attributes_with_prices = []
	for (var item_edit_row of items_edit_rows) {
		var attr_select = $(item_edit_row).find('select[data-fieldname^=attribute_select]')
		var mrp_input = $(item_edit_row).find('input[data-fieldname^=mrp_rate]')
		var pur_input = $(item_edit_row).find('input[data-fieldname^=buying_rate]')
		var qty_input = $(item_edit_row).find('input[data-fieldname^=qty]')

		if (pur_input.length != 1 || mrp_input.length != 1 || qty_input.length != 1 || attr_select.length != 1) {
			continue
		}

		var attr = attr_select[0].value
		var mrp = mrp_input[0].value
		var rate = pur_input[0].value
		var qty = qty_input[0].value

		item_attributes_with_prices.push({
			qty: qty,
			rate: rate,
			mrp: mrp,
			attr: attr
		})
	}

	return {
		item_name: item_name,
		item_group: item_group,
		article: article,
		brand: brand,
		hsn: hsn,
		item_attr: item_attribute,
		company: company,
		item_attributes_with_prices: item_attributes_with_prices
	}
}

function create_item_edit_table(purchase_rate, item_attribute_values, html_wrapper) {
	html_wrapper.html('<table id="items_edit" style="width:100%"><col width=30%><col width=25%><col width=25%><col width=20%><thead><tr><th>Attribute</th><th style="text-align:right">Pr. Rate</th><th style="text-align:right">Sell Rate</th><th style="text-align:right">Qty</th></tr></thead><tbody id="items_edit_body"></tbody></table>')
	var items_edit_table = $('#items_edit_body')[0]
	if (items_edit_table) {
		var option_string = ''
		for (var item_attribute_value in item_attribute_values) {
			option_string += `<option value="${item_attribute_value}">${item_attribute_value}</option>`
		}
		for (var item_attribute_value in item_attribute_values) {

			// Adding Size Attribute Selections
			var sell_rate = item_attribute_values[item_attribute_value]
			var row = items_edit_table.insertRow(-1)
			var col = row.insertCell(-1)
			col.innerHTML = `<select class="input-with-feedback form-control" data-fieldname="attribute_select"></select>`
			var select_item = $(col).find('select')[0]
			$(select_item).append($(option_string))
			$(select_item).val(item_attribute_value)

			// Adding Purchase, Sales and Quantity Inputs
			var col = row.insertCell(-1)
			col.innerHTML = `<input type="number" autocomplete="off" class="input-with-feedback form-control bold" data-fieldtype="Currency" data-fieldname="buying_rate" placeholder="" style="text-align:right" value=${purchase_rate}>`
			var col = row.insertCell(-1)
			col.innerHTML = `<input type="number" autocomplete="off" class="input-with-feedback form-control bold" data-fieldtype="Currency" data-fieldname="mrp_rate" placeholder="" style="text-align:right" value=${sell_rate}>`
			var col = row.insertCell(-1)
			col.innerHTML = `<input type="number" autocomplete="off" class="input-with-feedback form-control bold" data-fieldtype="Currency" data-fieldname="qty" placeholder="" style="text-align:right" value=0>`
		}
	}
}

function create_numerical_sizes(d) {
	var from_size = d.fields_dict.from_size.get_value()
	var to_size = d.fields_dict.to_size.get_value()
	var increment = d.fields_dict.increment.get_value()
	var price_jump = d.fields_dict.price_jump.get_value()
	var sell_rate = d.fields_dict.sell_rate.get_value()

	if ((!from_size && from_size !=0) || Number(from_size) == NaN) {
		frappe.msgprint('Enter From Size in Proper format')
	}

	if (!to_size || Number(to_size) == NaN) {
		frappe.msgprint('Enter To Size in Proper format')
	}

	if (!increment || Number(increment) == NaN) {
		frappe.msgprint('Enter Increment in Proper format')
	}

	if ((!price_jump && price_jump != 0) || Number(price_jump) == NaN) {
		frappe.msgprint('Enter Price Jump in Proper format')
	}

	if (!sell_rate || Number(sell_rate) == NaN) {
		frappe.msgprint('Enter Selling Rate in Proper format')
	}

	if (to_size <= from_size) {
		frappe.msgprint("To Size Cannot be less than or same as From size")
	}

	var size_price_map = {}
	var sell_rate_base = sell_rate - Number(price_jump)

	for (var v_size = Number(from_size); v_size <= Number(to_size); v_size = v_size + Number(increment)) {
		sell_rate_base = sell_rate_base + Number(price_jump)
		size_price_map[v_size] = sell_rate_base
	}

	return size_price_map
}

function open_item_helper(frm) {
	if (!frm.doc.supplier) {
		frappe.msgprint('Select Supplier First')
		return
	}

	frappe.dom.freeze()
	frappe.db.get_list('Item Attribute')
		.then(function (item_attributes) {
			frappe.dom.unfreeze()
			var item_attribute_select_options = []
			for (var item_attribute of item_attributes) {
				item_attribute_select_options.push(item_attribute.name)
			}
			var d = new frappe.ui.Dialog({
				'fields': [
					{ 'fieldname': 'item_name', 'fieldtype': 'Data', 'options': '', "label": "New Item", reqd: 1 },
					{ 'fieldname': 'article', 'fieldtype': 'Data', 'options': '', "label": "Article", reqd: 1 },
					{ 'fieldname': 'item_group', 'fieldtype': 'Link', 'options': 'Item Group', "label": "Item Group", reqd: 1 },
					{ 'fieldname': 'brand', 'fieldtype': 'Link', 'options': 'Brand', "label": "Brand" },
					{ 'fieldname': 'col1', 'fieldtype': 'Column Break', 'options': '', reqd: 1 },
					{ 'fieldname': 'hsn', 'fieldtype': 'Link', 'options': 'GST HSN Code', "label": "HSN"},
					{ 'fieldname': 'rate', 'fieldtype': 'Currency', 'options': '', "label": "Purchase Rate", reqd: 1 },
					{ 'fieldname': 'percent', 'fieldtype': 'Float', 'options': '', "label": "Add Margin (%)" },
					{ 'fieldname': 'sell_rate', 'fieldtype': 'Currency', 'options': '', "label": "Selling Rate", reqd: 1 },
					{ 'fieldname': 'sec1', 'fieldtype': 'Section Break', 'options': '', "label": "Size", reqd: 1 },
					{ 'fieldname': 'item_attribute_select', 'fieldtype': 'Select', 'options': item_attribute_select_options, "label": "Select Size", reqd: 1 },
					{ 'fieldname': 'is_numeric', 'fieldtype': 'Data', 'default': 0, hidden: 1 },
					{ 'fieldname': 'from_size', 'fieldtype': 'Int', 'options': '', "label": "From Size", depends_on: 'eval:doc.is_numeric==1' },
					{ 'fieldname': 'to_size', 'fieldtype': 'Int', 'options': '', "label": "To Size", depends_on: 'eval:doc.is_numeric==1' },
					{ 'fieldname': 'col2', 'fieldtype': 'Column Break', 'options': '', reqd: 1, hidden: 1 },
					{ 'fieldname': 'increment', 'fieldtype': 'Int', 'options': '', "label": "Increment", depends_on: 'eval:doc.is_numeric==1' },
					{ 'fieldname': 'price_jump', 'fieldtype': 'Currency', 'options': '', "label": "Price Jump", depends_on: 'eval:doc.is_numeric==1' },
					{ 'fieldname': 'create_num_items', 'fieldtype': 'Button', 'options': '', "label": "Create Items", depends_on: 'eval:doc.is_numeric==1' },
					{ 'fieldname': 'sec2', 'fieldtype': 'Section Break', 'options': '', "label": "Items", reqd: 1 },
					{ 'fieldname': 'item_html', 'fieldtype': 'HTML', 'options': '', "label": "" },
				],
				title: 'Item Helper',
				primary_action: function () {
					d.set_message('Creating Items')
					var r = get_final_item_values(d, frm.doc.company)
					frappe.call({
						method: 'erpnext_retail.items.items.add_items',
						args: {
							doc: frm.doc,
							item_attribute: r.item_attr,
							company: r.company,
							item_price_array: r.item_attributes_with_prices,
							item_name: `${r.item_name} ${r.article}`,
							item_group: r.item_group,
							article: r.article,
							brand: r.brand,
							hsn: r.hsn,
							purchase_invoice_doc: frm.doc.name
						}
					}).then(function (r) {
						if (!r.message) {
							frappe.msgprint('Error')
						} else {
							frappe.model.sync(r.message)
							frm.refresh()
							d.clear()
							$('#items_edit').remove()
						}
						// correct_item_taxes(frm)
						d.clear_message()

					})
				}
			});
			d.fields_dict.create_num_items.onclick = () => {
				var size_price_map = create_numerical_sizes(d)
				var rate = d.fields_dict.rate.get_value()
				create_item_edit_table(rate, size_price_map, d.fields_dict.item_html)
			}
			d.fields_dict.rate.df.onchange = () => {
				caluclate_selling_price(d)
			}
			d.fields_dict.percent.df.onchange = () => {
				caluclate_selling_price(d)
			}
			d.fields_dict.sell_rate.df.onchange = () => {
				update_prices(d)
			}
			d.fields_dict.item_attribute_select.df.onchange = () => {
				frappe.dom.freeze()
				$('#items_edit').remove()
				var selected_value = d.fields_dict.item_attribute_select.get_value()
				frappe.db.get_doc('Item Attribute', selected_value)
					.then(function (item_attribute_doc) {
						frappe.dom.unfreeze()
						var is_numeric = item_attribute_doc.numeric_values

						var item_attribute_values = {}
						if (is_numeric) {
							d.set_value('is_numeric', 1)
						} else {
							d.set_value('is_numeric', 0)
							var sell_rate = d.fields_dict.sell_rate.get_value()
							var rate = d.fields_dict.rate.get_value()

							for (var item_attribute_value of item_attribute_doc.item_attribute_values) {
								item_attribute_values[item_attribute_value.attribute_value] = Number(sell_rate)
							}

							create_item_edit_table(rate, item_attribute_values, d.fields_dict.item_html)
						}

					}).catch(function (err) {
						frappe.dom.unfreeze()
						frappe.msgprint(err)
					})
			}
			d.show();
		}).catch(function (err) {
			frappe.msgprint(err)
			frappe.dom.unfreeze()
		})

}

frappe.ui.form.on('Purchase Invoice', {
	refresh(frm) {
		if (frm.doc.status != 1) {
			frm.add_custom_button("Item Helper New", function () {
				open_item_helper(frm)
			})
		}

		if (frm.doc.docstatus == 1 || frm.doc.docstatus == 2) {
			frm.add_custom_button('Print Barcodes', function () {
				var pi_items = frm.doc.items
				var company = frm.doc.company
				frappe.new_doc('Item Barcode Print')
					.then(function () {
						frappe.dom.freeze('Loading Please Wait')
						cur_frm.set_value('company', company)

						if (cur_frm.doc.items.length > 0) {
							while (cur_frm.doc.items.length > 0) {
								cur_frm.doc.items.pop()
							}
						}

						cur_frm.refresh_field('items')

						for (var pi_item of pi_items) {
							if(pi_item.item_group == 'TRANSPORT EXP') {
								continue
							}
							var child_table = frappe.model.add_child(cur_frm.doc, "Barcode Print Items", "items")
							frappe.model.set_value(child_table.doctype, child_table.name, 'item', pi_item.item_code)
							frappe.model.set_value(child_table.doctype, child_table.name, 'number_of_print', pi_item.received_qty)
						}

						cur_frm.set_value('total_items', cur_frm.doc.items.length)
						cur_frm.refresh_field('items')
					})
			})
		}
	}
})

// function correct_item_taxes(frm) {
// 	var place_of_supply = frm.doc.place_of_supply
// 	var supplier_gstin = frm.doc.supplier_gstin
// 	var bypass_gst_comparition = false
// 	var company = frm.doc.company

// 	if ((!place_of_supply) || (!supplier_gstin)) {
// 		bypass_gst_comparition = true
// 	}

// 	for (var item of frm.doc.items) {
// 		var row = item

// 		if(row.item_group){
// 			var item_group_lowercase = row.item_group.toLocaleLowerCase()
// 			if(item_group_lowercase.indexOf('saree') != -1) {
// 				frappe.model.set_value(row.doctype, row.name, "item_tax_template", '')
// 				continue
// 			}
// 		}

// 		if ((row.rate > 1000) && !bypass_gst_comparition) {
// 			var supplier_gst_location = supplier_gstin.substr(0, 2)
// 			var our_gst_location = place_of_supply.substr(0, 2)

// 			var is_inter_state = 0

// 			if (supplier_gst_location != our_gst_location) {
// 				is_inter_state = 1
// 			}

// 			if (is_inter_state == 1) {
// 				var item_tax_template = (company == 'Kothari Collections') ? "Out GST 12% - KC" : "Out GST 12% - KG"
// 				frappe.model.set_value(row.doctype, row.name, "item_tax_template", item_tax_template)
// 			} else {
// 				var item_tax_template = (company == 'Kothari Collections') ? "In GST 12% - KC" : "In GST 12% - KG"
// 				frappe.model.set_value(row.doctype, row.name, "item_tax_template", item_tax_template)
// 			}
// 		} else {
// 			if (row.rate > 1000) {
// 				var item_tax_template = (company == 'Kothari Collections') ? "In GST 12% - KC" : "In GST 12% - KG"
// 				frappe.model.set_value(row.doctype, row.name, "item_tax_template", item_tax_template)
// 			} else {
// 				frappe.model.set_value(row.doctype, row.name, "item_tax_template", '')
// 			}
// 		}
// 	}
// }

// frappe.ui.form.on('Purchase Invoice Item', "rate", function (frm, cdt, cdn) {
// 	correct_item_taxes(frm)
// })

// frappe.ui.form.on('Purchase Invoice', "refresh", function (frm) {
//     if(frm.doc.is_return == 1){
//         correct_item_taxes(frm)
//     }
// })
