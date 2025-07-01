// Copyright (c) 2025, Abaikarthik and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Person"] = {
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
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person",
		//	default: 'All',
			description: __("Select a specific sales person or leave as 'All' to include all sales persons.")
		}
	],
	onload: function (report) {
		// Get current user's roles
		let roles = frappe.user_roles;

		// Get the sales_person filter
		let filter = report.get_filter("sales_person");

		if (!filter) return;

		// If user has "Sales Manager" role, allow edit
		if (roles.includes("Sales Manager")) {
			// editable: do nothing (default)
			filter.df.read_only = 0;
		} else {
			// else freeze (read-only)
			filter.df.hidden = 1;
			filter.df.read_only = 1;
			filter.refresh();
		}
	}

};
