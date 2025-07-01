// Copyright (c) 2025, Abaikarthik and contributors
// For license information, please see license.txt

frappe.query_reports["Service Report"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			width: "80",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "supplier",
			label: __("supplier"),
			fieldtype: "Link",
			options: "Supplier",
		},
		{
			fieldname: "service_status",
			label: __("Service Status"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "Product Inward", label: __("Product Inward") },
				{ value: "Issue Identified", label: __("Issue Identified") },
				{ value: "Dispatch Product", label: __("Dispatch Product") },
				{ value: "Dispatch Spare", label: __("Dispatch Spare") },
				{ value: "In-House Preparation", label: __("In-House Preparation") },
				{ value: "Product Received", label: __("Product Received") },
				{ value: "Return To Customer", label: __("Return To Customer") },
				{ value: "Ready for Delivery", label: __("Ready for Delivery") },
				{ value: "To Delivery", label: __("To Delivery") },
				{ value: "To Invoice", label: __("To Invoice") },
				{ value: "Completed", label: __("Completed") },
				{ value: "Ready to Dispatch", label: __("Ready to Dispatch") },
				{ value: "Update Used Spare", label: __("Update Used Spare") }
			],
		},
		// {
		// 	fieldname: "service_type",
		// 	label: __("Service Type"),
		// 	fieldtype: "Select",
		// 	options: [
		// 		{ value: "", label: __("") },
		// 		{ value: "Dispatch Product", label: __("Dispatch Product") },
		// 		{ value: "Dispatch Spare", label: __("Dispatch Spare") },
		// 		{ value: "In-House Preparation", label: __("In-House Preparation") },
		// 	],
		// },
		{
			fieldname: "service_person",
			label: __("Service Person"),
			fieldtype: "Link",
			options: "User",
			get_query: () => {
				return {
					filters: {
						role_profile_name: "Service Team"
					}
				};
			}
		}


	]
};
