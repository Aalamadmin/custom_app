import frappe
from frappe import _, msgprint
from pypika import Order


def execute(filters: dict | None = None):
	columns = get_columns()
	data = get_data(filters)

	for row in data:
		# Convert invoice string to dynamic links
		row["invoices"] = generate_invoice_links(row.get("invoices", ""))

	frappe.errprint("data:"+ str(data))

	return columns, data

def generate_invoice_links(invoice_str):
    if not invoice_str:
        return ""

    # Ensure it's a list even if it's just one invoice
    invoice_list = [inv.strip() for inv in invoice_str.split(",") if inv.strip()]
    
    # Convert each to a dynamic link
    links = [
        f'<a href="/app/sales-invoice/{inv}" target="_blank">{inv}</a>'
        for inv in invoice_list
    ]
    
    return ", ".join(links)

def get_columns() -> list[dict]:
	return [
		{
			"label": _("Sales Order"),
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
		},
		{
			"label": _("Sales Invoices"),
			"fieldname": "invoices",
			"fieldtype": "Data",
			"options": "Sales Invoice",
		},
		{
			"label": _("Order Date"),
			"fieldname": "order_date",
			"fieldtype": "Date",
			"options": "Order Date",
		},
		{
			"label": _("Sales Person"),
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"label": _("Order Amount"),
			"fieldname": "order_amount",
			"fieldtype": "Currency",
			"options": "currency"
		},
		{
			"label": _("Bill Amount"),
			"fieldname": "bill_amount",
			"fieldtype": "Currency",
			"options": "currency"
		},
		{
			"label": _("Balance Amount"),
			"fieldname": "balance_amount",
			"fieldtype": "Currency",
			"options": "currency"
		}

	]

def get_data(filters) -> list[list]:
	filters = dict(filters) if filters else {}
	frappe.errprint(frappe.get_roles())
	frappe.errprint(frappe.session.user)

	# if filters.get("sales_person") and "Sales Manager" not in frappe.get_roles():
	# 	sales_persons = frappe.get_all(
	# 		"Sales Person",
	# 		filters={"custom_sales_person_email": frappe.session.user},
	# 		fields=["name"]
	# 	)
	# 	filters["sales_person"] = sales_persons[0]["name"] if sales_persons else None
	
	if "Sales Manager" not in frappe.get_roles():
		sales_persons = frappe.get_all(
			"Sales Person",
			filters={"custom_sales_person_email": frappe.session.user},
			fields=["name"]
		)
		filters["sales_person"] = sales_persons[0]["name"] if sales_persons else "__no_access__"

	if filters.get("sales_person") == "__no_access__":
		msgprint(_("You are not authorized to view this report."))
		return []
	
	# elif "Sales Manager" in frappe.get_roles():
	# 	if filters.get("sales_person") and filters["sales_person"].lower() == "all":
	# 		filters["sales_person"] = None

	query = """
	SELECT
		st.parent AS sales_order,
		GROUP_CONCAT(DISTINCT si.name ORDER BY si.name SEPARATOR ',') AS invoices,
		so.transaction_date AS order_date,
		st.sales_person,
		st.allocated_amount AS order_amount,
		SUM(si.net_total) AS bill_amount,
		st.allocated_amount - SUM(si.net_total) AS balance_amount
	FROM
		`tabSales Team` st
	JOIN `tabSales Order` so ON st.parent = so.name
	JOIN `tabSales Invoice Item` sii ON sii.sales_order = st.parent
	JOIN `tabSales Invoice` si ON si.name = sii.parent
	WHERE st.parenttype = 'Sales Order'
	"""

	if filters.get("from_date"):
		query += " AND so.transaction_date >= %(from_date)s"
	if filters.get("to_date"):
		query += " AND so.transaction_date <= %(to_date)s"
	if filters.get("sales_person"):
		query += " AND st.sales_person = %(sales_person)s"

	query += """
	GROUP BY st.parent
	"""

	frappe.errprint(query)
	frappe.errprint(filters)

	return frappe.db.sql(query, filters, as_dict=True)

