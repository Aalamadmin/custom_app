from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote
from frappe import _
import frappe

class DeliveryNoteValidation(DeliveryNote):
    def so_required(self):
        """check in manage account if sales order required or not"""
        if frappe.db.get_single_value("Selling Settings", "so_required") == "Yes":
            for d in self.get("items"):
                if not (d.against_sales_order or d.custom_against_service_request):
                    frappe.throw(_("Sales Order Or Service Request is required for Item {0}").format(d.item_code))
