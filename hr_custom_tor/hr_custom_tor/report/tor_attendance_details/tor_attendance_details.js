// Copyright (c) 2025, IECMU and contributors
// For license information, please see license.txt

function pad(num, size) {
  num = num.toString();
  while (num.length < size) num = "0" + num;
  return num;
}

function fmt(date) {
  const year = date.getFullYear();
  const month = date.getMonth() + 1; // Zero index
  const day = date.getDate();
  return `${year}-${pad(month,2)}-${pad(day,2)}`; //Format to yyyy-mm-dd
}

frappe.query_reports["Tor Attendance Details"] = {
  filters: [
    {
      fieldname: "start_date",
      fieldtype: "Date",
      label: "Start Date",
      mandatory: 1,
      wildcard_filter: 0,

      on_change: function (query_report) {
        const is_whole_month = query_report.get_filter_value("is_whole_month");

        if (!is_whole_month) {
          return;
        }

        const start_date = query_report.get_filter_value("start_date");
        const date = new Date(start_date);

        // Get first and last day of the month
        const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);

        query_report.set_filter_value("start_date", fmt(firstDay));
        query_report.set_filter_value("end_date", fmt(lastDay));
        // console.log({
        //   start_date,
        //   fd: fmt(firstDay),
        //   ld: fmt(lastDay),
        //   query_report,
        // });

        const monthStr = date.toLocaleString("default", { month: "long" });
        const year = date.getFullYear();
        frappe.show_alert(
          `The start and end date has been set to the month of ${monthStr} ${year}`,
          5
        );

        // Without this the report will be stale
        query_report.refresh();

        // frappe.query_report.toggle_filter_display(
        // 	"supplier_group",
        // 	frappe.query_report.get_filter_value("party_type") !== "Supplier"
        // );
        // query_report.refresh_report(filters);
      },
    },
    {
      fieldname: "end_date",
      fieldtype: "Date",
      label: "End Date",
      read_only: 1,
      mandatory: 1,
      wildcard_filter: 0,
    },

    // {
    //   fieldname: "employee_name",
    //   fieldtype: "Link",
    //   options: "Employee",
    //   label: "พนักงาน",
    //   mandatory: 0,
    //   wildcard_filter: 0,
    // },

    {
      fieldname: "employee_names",
      label: "พนักงาน",
      fieldtype: "MultiSelectList",
      width: "100",
      get_data: function (txt) {
        return frappe.db.get_link_options("Employee", txt);
      },
    },

    {
      fieldname: "is_summary",
      label: "Summary",
      fieldtype: "Check",
      mandatory: 0,
      default: "0",
    },

    {
      fieldname: "is_whole_month",
      label: "เลือกทั้งเดือน",
      fieldtype: "Check",
      mandatory: 0,
      default: "1",
    },
  ],
};
