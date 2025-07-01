// Copyright (c) 2025, Abaikarthik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Warranty Status', {
    refresh: function (frm) {
        frm.disable_save()
    },
    check: function (frm) {
        if (!frm.doc.serial_no) {
            frappe.msgprint(__('Please enter a Serial No.'));
            return;
        }

        frappe.call({
            method: 'custom_app.custom_app.doctype.item_warranty_status.item_warranty_status.get_purchase_details',
            args: {
                serial_no: frm.doc.serial_no
            },
            callback: function (r) {
                if (r.message) {
                    console.log(r.message);
                    const details = r.message;
                    const dialog = new frappe.ui.Dialog({
                        title: 'Purchase Receipt Details',
                        fields: [
                            { label: 'Purchase Receipt', fieldtype: 'Link', Option: "Purchase Receipt", read_only: 1, default: details.purchase_details.name },
                            { label: 'Purchase Order', fieldtype: 'Link', options: "Purchase Order", read_only: 1, default: details.purchase_details.purchase_order },
                            { label: 'Delivery Note', fieldtype: 'Link', options: "Delivery Note", read_only: 1, default: details.sales_details.name },
                            { label: 'Sales Order', fieldtype: 'Link', options: "Sales Order", read_only: 1, default: details.sales_details.sales_order },
                            { label: 'Serial Batch ID', fieldtype: 'Link', options: "Serial and Batch Bundle", read_only: 1, default: details.serial_and_batch_bundle_id },
                            { fieldtype: 'Column Break' },  // Moves next fields to the second column
                            { label: 'Receipt Date', fieldtype: 'Date', read_only: 1, default: details.purchase_details.posting_date },
                            { label: 'Supplier', fieldtype: 'Data', read_only: 1, default: details.purchase_details.supplier_name },
                            { label: 'Delivery Date', fieldtype: 'Date', read_only: 1, default: details.sales_details.posting_date },
                            { label: 'Customer', fieldtype: 'Data', read_only: 1, default: details.sales_details.customer },
                            { label: 'Serial', fieldtype: 'Link', options: "Serial No", read_only: 1, default: details.serial_no },
                        ]
                    });
                    dialog.show();
                } else {
                    frappe.msgprint(__('The transaction is not fully covered. Check the <a href="/app/query-report/Serial No Ledger" target="_blank">Serial No Ledger</a> report for details.'));
                }
            }
        });
    }
});

