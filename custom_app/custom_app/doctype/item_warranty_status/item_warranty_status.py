# Copyright (c) 2025, Abaikarthik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemWarrantyStatus(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_purchase_details(serial_no):
    try:
        # Existing code with added error logging
        serial_no = serial_no.strip() 
        frappe.log_error(f"Processing serial no: {serial_no}")
        d = frappe.db.get_list(
            "Serial No",
            filters={"name": serial_no, "status": "Delivered"},
            fields=["name", "purchase_document_no"]
        )

        if not d:
            frappe.log_error(f"No Serial No found for {serial_no}")
            return

        purchase_document_no = d[0].get("purchase_document_no")

        if not purchase_document_no:
            frappe.log_error(f"No purchase document for serial no {serial_no}")
            return

        details = frappe.db.get_list(
            "Purchase Receipt",
            filters={"name": purchase_document_no},
            fields=["name", "supplier_name", "lr_date","posting_date"]
        )

        purchase_details = details[0] if details else None

        bundle_details = frappe.db.get_all(
            "Serial and Batch Entry",
            filters={"serial_no": serial_no, "is_outward": 1},
            fields=["parent"]
        )

        serial_and_batch_bundle_id = bundle_details[0]["parent"] if bundle_details else None

        dn_details = frappe.db.get_all(
            "Serial and Batch Bundle",
            filters={"name": serial_and_batch_bundle_id},
            fields=["voucher_no", "voucher_type"]
        )

        dn_id = dn_details[0]["voucher_no"] if dn_details else None

        delivery_note_details = frappe.db.get_all(
            "Delivery Note",
            filters={"name": dn_id},
            fields=["customer", "posting_date","name"]
        )

        delivery_note = delivery_note_details[0] if delivery_note_details else None
        #Get Sales order details
        delivery_note_items=None
        if dn_id:
            delivery_note_items = frappe.get_all(
            "Delivery Note Item",
            filters={
                "parent": dn_id.strip,
                "parenttype": "Delivery Note",
                "parentfield": "items"
            },
            fields=["against_sales_order"]
        )
        if delivery_note_items:
            delivery_note["sales_order"]= delivery_note_items[0].get("against_sales_order") if delivery_note_items[0].get("against_sales_order") else None

        #Get Purchase order details
        purchase_order_details = None

        if purchase_document_no:  # Make sure pr_name is your Purchase Receipt name (e.g. "PR-0001")
            pr_items = frappe.get_all(
                "Purchase Receipt Item",
                filters={
                    "parent": purchase_document_no.strip(),  # Use () to call .strip
                    "parenttype": "Purchase Receipt",
                    "parentfield": "items"
                },
                fields=["purchase_order"]
            )
            if pr_items:
                purchase_order_details = pr_items[0].get("purchase_order") if pr_items[0].get("purchase_order") else None
                purchase_details["purchase_order"] = purchase_order_details
            


        return {
            "purchase_details": purchase_details,
            "serial_and_batch_bundle_id": serial_and_batch_bundle_id,
            "serial_no": serial_no,
            "sales_details": delivery_note 
        }

    except Exception as e:
        frappe.log_error(f"Error in get_purchase_details: {str(e)}")
        return {"error": str(e)}
