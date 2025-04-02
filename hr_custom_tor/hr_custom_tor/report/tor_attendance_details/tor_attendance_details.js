// Copyright (c) 2025, IECMU and contributors
// For license information, please see license.txt

frappe.query_reports["Tor Attendance Details"] = {


	"filters": [
		{
			fieldname: "start_date",
			fieldtype: "Date",
			label: "Start Date",
			mandatory: 1,
			wildcard_filter: 0,

			on_change: function () {
				// frappe.query_report.set_filter_value("party", "");
				// frappe.query_report.toggle_filter_display(
				// 	"supplier_group",
				// 	frappe.query_report.get_filter_value("party_type") !== "Supplier"
				// );
				console.log(
					"changed"
				)
			},
		},
		{
			fieldname: "end_date",
			fieldtype: "Date",
			label: "End Date",
			mandatory: 1,
			wildcard_filter: 0,
		},

	]
};
