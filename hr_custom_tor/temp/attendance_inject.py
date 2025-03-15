# Copyright (c) 2025, CMU and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


def findEmployee(searchStr):
    searchStr = searchStr.strip()
    name = frappe.db.exists(
        "Employee",
        {
            "first_name": searchStr,
        },
    )

    if name:
        return name

    name = frappe.db.exists(
        "Employee",
        {
            "last_name": searchStr,
        },
    )

    if name:
        return name

    name = frappe.db.exists(
        "Employee",
        {
            "employee_name": searchStr,
        },
    )

    if name:
        return name
    else:
        return None


class TorDrink(Document):
    def before_save(self):
        emp = "EMPA"
        attDate = getdate("2025-03-01")
        lateTime = 200

        empName = findEmployee(emp)
        if not empName:
            frappe.throw(f"No Employee {emp}")
        name = frappe.db.exists(
            "Attendance",
            {
                "employee": empName,
                "attendance_date": attDate,
            },
        )
        if name:
            frappe.db.set_value("Attendance", name, "custom_late_time", lateTime)
        else:
            newAtt = frappe.get_doc(
                {
                    "doctype": "Attendance",
                    "employee": empName,
                    "attendance_date": attDate,
                    "custom_late_time": lateTime,
                    "status": "Present",
                    "docstatus": 1,
                }
            )
            newAtt.insert()
