# Copyright (c) 2025, Abaikarthik and contributors
# For license information, please see license.txt
import frappe
from frappe import _, msgprint
from pypika import Order


def execute(filters: dict | None = None):
	columns = get_columns()
	service_request_list = get_data(filters)

	if len(service_request_list) > 0:
		for service_request in service_request_list:
			if service_request.service_status  in ["Completed", "To Invoice"]:
				invoice=get_invoice_details(service_request.service_request)
				if invoice:
					service_request.invoice = invoice[0].invoice
					service_request.posting_date = invoice[0].posting_date
					service_request.grand_total = invoice[0].grand_total
					frappe.errprint(invoice)
			else:
				service_request.invoice = None
				service_request.posting_date = None
				service_request.grand_total = None


	return columns, service_request_list


def get_columns() -> list[dict]:

	return [
		{
			"label": _("Service Request"),
			"fieldname": "service_request",
			"fieldtype": "Link",
			"options": "Service Request",
		},
		{
			"label": _("Service Status"),
			"fieldname": "service_status",
			"fieldtype": "Data",
			"options": "Service Status",
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"label": _("Customer Address"),
			"fieldname": "customer_address",
			"fieldtype": "Link",
			"options": "Address"
		},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"label": _("Supplier Address"),
			"fieldname": "supplier_address",
			"fieldtype": "Link",
			"options": "Address"
		},
		{
			"label": _("RMI Number"),
			"fieldname": "rmi_number",
			"fieldtype": "Data",
			"options": "RMI Number",
		},
		{
			"label": _("Contact Person"),
			"fieldname": "contact_person",
			"fieldtype": "Data",
			"options": "Contact"
		},
		{
			"label": _("Phone No"),
			"fieldname": "phone_no",
			"fieldtype": "Data",
			"options": "Phone No",
		},
		{
			"label": _("Service Person"),
			"fieldname": "service_person",
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"label": _("Approx Amount"),
			"fieldname": "approx_amount",
			"fieldtype": "Currency",
			"options": "currency"
		},
		{
			"label": _("Invoice"),
			"fieldname": "invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice"	
		},
		{
			"label": _("grand_total"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"options": "currency"
		},
		{
			"label": _("Transaction Start Date"),
			"fieldname": "transaction_start_date",
			"fieldtype": "Date",
			"options": "Transaction Start Date"
		},
		{
			"label": _("Transaction End Date"),
			"fieldname": "transaction_end_date",
			"fieldtype": "Date",
			"options": "Transaction End Date"
		}

	]


def get_data(filters) -> list[list]:
	filters = dict(filters) if filters else {}

	query = """
	select
	t.name as 'service_request',
	t.service_status,
	t.customer,
	t.customer_address,
	t.supplier,
	t.supplier_address, 
	t.rmi_number,
	t.contact_person,
	t.phone_no ,
	t2.full_name ,
	t.approx_amount,
	t.transaction_start_date,
	t.transaction_end_date
from
	`tabService Request` t
inner join `tabUser` t2 on t2.name = t.service_person
WHERE
	t.docstatus = 1
	"""

	if filters.get("service_status"):
		query += " AND t.service_status = %(service_status)s"
	if filters.get("customer"):
		query += " AND t.customer = %(customer)s"
	if filters.get("supplier"):
		query += " AND t.supplier = %(supplier)s"
	if filters.get("from_date"):
		query += " AND (t.creation >= %(from_date)s)"
	if filters.get("to_date"):
		query += " AND t.creation <= %(to_date)s"
	if filters.get("service_person"):
		query += " AND t.service_person = %(service_person)s"
	if filters.get("rmi_number"):
		query += " AND t.rmi_number = %(rmi_number)s"

	query += " ORDER BY t.creation DESC"

	return frappe.db.sql(query, filters, as_dict=True)

def get_invoice_details(service_request):
	"""
	Get invoice details for a given service request.
	"""
	query = """
	SELECT
		t1.name as 'invoice',
		t1.posting_date as 'posting_date',
		t1.grand_total as 'grand_total'
	FROM
		`tabSales Invoice` t1
	INNER JOIN `tabSales Invoice Item` t2 ON t1.name = t2.parent
	WHERE
		t2.custom_service_request = %s
	"""
	return frappe.db.sql(query, service_request, as_dict=True)

