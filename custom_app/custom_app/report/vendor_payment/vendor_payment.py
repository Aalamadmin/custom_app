import frappe
from frappe import _, msgprint
from pypika import Order


def execute(filters: dict | None = None):
	columns = get_columns()
	service_request_list = get_data(filters)
	if not service_request_list:
		msgprint(_("No records found"), alert=True)
		return columns, service_request_list
	return columns, service_request_list


def get_columns() -> list[dict]:

	return [
		{
			"label": _("Purchase Order"),
			"fieldname": "purchase_order",	
			"fieldtype": "Link",
			"options": "Purchase Order",	
		},
		{	
			"label": _("Purchase Order Date"),
			"fieldname": "po_date",
			"fieldtype": "Date",
		},
		{			
			"label": _("Purchase Order Status"),
			"fieldname": "po_status",
			"fieldtype": "Data"
		},
		{
			"label": _("Purchase Receipt"),
			"fieldname": "purchase_receipt",
			"fieldtype": "Link",
			"options": "Purchase Receipt",
		},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data"
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item"
		},
		# {
		# 	"label": _("Qty"),
		# 	"fieldname": "qty",
		# 	"fieldtype": "Float"
		# },
		{
			"label": _("Purchase Price"),
			"fieldname": "purchase_price",
			"fieldtype": "Currency"
		},
		{
			"label": _("Serial No"),
			"fieldname": "serial_no",
			"fieldtype": "Data"
		},
		{
			"label": _("Serial Status"),
			"fieldname": "status",
			"fieldtype": "Data"
		},
		{
			"label": _("Sales Order"),
			"fieldname": "against_sales_order",
			"fieldtype": "Link",
			"options": "Sales Order"
		},
		{
			"label": _("Order Status"),
			"fieldname": "billing_status",
			"fieldtype": "Data"
		},
		{
			"label": _("Delivery Note"),
			"fieldname": "delivery_note",
			"fieldtype": "Link",
			"options": "Delivery Note"
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"label": _("Sales Rate"),
			"fieldname": "sales_rate",
			"fieldtype": "Currency"
		},
		{
			"label": _("Sales Person"),
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"label": _("Sales Person Email"),
			"fieldname": "sales_person_email",
			"fieldtype": "Data"
		}	
	]


def get_data(filters) -> list[list]:
	filters = dict(filters) if filters else {}

	# Base query to fetch purchase orders, receipts, items, and serial numbers
	query="""
WITH Purchase_completed AS (
    SELECT
        tpo.name AS purchase_order,
        tpo.transaction_date,
        tpo.status AS po_status,
        pr.name AS purchase_receipt,
        pr.supplier,
        pri.item_name,
        pri.item_code,
        pri.qty,
        pri.rate,
        sbpr.name AS serial_batch_bundle,
        tsabe.serial_no,
        tsn.status
    FROM `tabPurchase Receipt` pr
    LEFT JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
    LEFT JOIN `tabPurchase Order` tpo ON tpo.name = pri.purchase_order
    LEFT JOIN `tabSerial and Batch Bundle` sbpr ON pri.serial_and_batch_bundle = sbpr.name
    INNER JOIN `tabSerial and Batch Entry` tsabe ON tsabe.parent = sbpr.name AND tsabe.is_outward = 0
    INNER JOIN `tabSerial No` tsn ON tsabe.serial_no = tsn.serial_no
    WHERE pr.docstatus = 1 
),
latest_serials AS (
    SELECT serial_no, MAX(transaction_date) AS latest_date
    FROM (
        SELECT
            tpo.transaction_date,
            tsabe.serial_no
        FROM `tabPurchase Receipt` pr
        LEFT JOIN `tabPurchase Receipt Item` pri ON pr.name = pri.parent
        LEFT JOIN `tabPurchase Order` tpo ON tpo.name = pri.purchase_order
        LEFT JOIN `tabSerial and Batch Bundle` sbpr ON pri.serial_and_batch_bundle = sbpr.name
        INNER JOIN `tabSerial and Batch Entry` tsabe ON tsabe.parent = sbpr.name AND tsabe.is_outward = 0
        WHERE pr.docstatus = 1 
    ) AS sub
    GROUP BY serial_no
),
sale_details AS (
    SELECT
        distinct t1.serial_no,
        t1.is_outward,
        t1.warehouse,
        t1.parent,
        t2.voucher_no,
        t2.voucher_type,
        t3.name AS delivery_note,
        t3.customer,
        tdni.against_sales_order
    FROM `tabSerial and Batch Entry` t1
    INNER JOIN `tabSerial and Batch Bundle` t2 ON t1.parent = t2.name
    LEFT JOIN `tabDelivery Note` t3 ON t3.name = t2.voucher_no
        AND t2.voucher_type = 'Delivery Note'
        AND t3.docstatus = 1 and t3.status != 'Return Issued'
    INNER JOIN `tabDelivery Note Item` tdni ON t3.name = tdni.parent
    WHERE t1.is_outward = 1 
),
sales_order_detail AS (
    SELECT
        tso.name AS so_name,
        tsoi.item_code,
        tsoi.rate,
        tst.sales_person,
        tsp.custom_sales_person_email,
        tso.status AS so_status,
        tso.billing_status,
        tso.delivery_status
    FROM `tabSales Order` tso
    INNER JOIN `tabSales Order Item` tsoi ON tso.name = tsoi.parent
    LEFT JOIN `tabSales Team` tst ON tst.parenttype = 'Sales Order' AND tst.parent = tso.name
    LEFT JOIN `tabSales Person` tsp ON tsp.sales_person_name = tst.sales_person
)

SELECT
    a.purchase_order,
    a.transaction_date AS po_date,
    a.po_status,
    a.purchase_receipt,
    a.supplier,
    a.item_name,
    a.item_code,
    a.qty,
    a.rate AS purchase_price,
    a.serial_batch_bundle,
    a.serial_no,
    a.status,
    b.is_outward,
    b.warehouse,
    b.parent,
    b.voucher_no,
    b.voucher_type,
    b.delivery_note,
    b.customer,
    b.against_sales_order,
    c.rate AS sales_rate,
    c.sales_person,
    c.custom_sales_person_email AS sales_person_email,
    c.billing_status,
    c.delivery_status
FROM
    Purchase_completed a
INNER JOIN latest_serials l ON
    a.serial_no = l.serial_no AND a.transaction_date = l.latest_date
LEFT JOIN sale_details b ON
    a.serial_no = b.serial_no
LEFT JOIN sales_order_detail c ON
    c.so_name = b.against_sales_order and a.item_code =c.item_code
"""

	if filters.get("from_date"):
		query += " where a.transaction_date >= %(from_date)s"
	if filters.get("to_date"):
		query += " and a.transaction_date <= %(to_date)s"
	if filters.get("supplier"):
		query += " and a.supplier = %(supplier)s"
	if filters.get("purchase_order"):
		query += " and a.purchase_order = %(purchase_order)s"
	if filters.get("item"):
		query += " and a.item_code = %(item)s"
	if filters.get("customer"):
		query += " and b.customer = %(customer)s"
	if filters.get("sales_person"):
		query += " and c.sales_person = %(sales_person)s"
	query += " order by a.transaction_date desc"

	return frappe.db.sql(query, filters, as_dict=True)

