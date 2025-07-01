# Copyright (c) 2025, Abaikarthik and contributors
# For license information, please see license.txt

# import frappe
#from frappe.model.document import Document
from frappe.model.document import Document
from frappe import _, msgprint
import frappe
from frappe.contacts.doctype.address.address import get_address_display

class ServiceRequest(Document):
	pass

@frappe.whitelist()
def get_display_address(address_name):
    """
    Get the display address for a given address name.
    """
    try:
        address = frappe.get_doc("Address", address_name)
        if not address:
            return {"status": "error", "message": _("Address not found.")}
        
        display_address = get_address_display(address.as_dict())
        if not display_address:
            return {"status": "error", "message": _("Display address not found.")}

        return {"status": "success", "display_address": display_address}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Display Address Error")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def check_draft(service_request_name):
    stock_entry = get_draft_stock_entries(service_request_name)
    delivery_notes = get_draft_delivery_notes(service_request_name)

    if stock_entry.get("status") == "success" and stock_entry.get("stock_entries"):
        links = [frappe.utils.get_link_to_form("Stock Entry", st) for st in stock_entry.get("stock_entries")]
        return {
            "status": "error",
            "message": _("Draft Stock Entry {0} must be submitted or cancelled before proceeding.").format(", ".join(links))
        }

    if delivery_notes.get("status") == "success" and delivery_notes.get("delivery_notes"):
        links = [frappe.utils.get_link_to_form("Delivery Note", dn) for dn in delivery_notes.get("delivery_notes")]
        return {
            "status": "error",
            "message": _("Draft Delivery Note {0} must be submitted or cancelled before proceeding.").format(", ".join(links))
        }

    return {"status": "ok"}

            


@frappe.whitelist()
def get_draft_stock_entries(service_request_name):
    """
    Get all draft Stock Entries linked to a Service Request.
    """
    stock_entries = frappe.db.sql(
        """SELECT name FROM `tabStock Entry`
        WHERE custom_service_request = %s AND docstatus = 0""",
        (service_request_name,),
        as_dict=True
    )
    
    if not stock_entries:
        return {"status": "success", "stock_entries": []}
    
    return {"status": "success", "stock_entries": [se.name for se in stock_entries]}

@frappe.whitelist()
def get_draft_delivery_notes(service_request_name):
    """
    Get all draft Delivery Notes linked to a Service Request.
    """
    delivery_notes = frappe.db.get_all(
        "Delivery Note",
        filters={
            "custom_service_request": service_request_name,
            "docstatus": 0
        },
        fields=["name"]
    )

    if not delivery_notes:
        return {"status": "success", "delivery_notes": []}
    # Return the names of the delivery notes
    # If you want to return more fields, you can modify the fields list in get_all    
    return {"status": "success", "delivery_notes": [dn.name for dn in delivery_notes]}
