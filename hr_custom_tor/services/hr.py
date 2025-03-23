# Copyright (c) 2025, CMU and contributors
# For license information, please see license.txt

import frappe


def findEmployee(searchStr, get_doc=False):
    name = findEmployeeName(searchStr)
    if name and get_doc:
        return frappe.get_doc("Employee", name)
    return name


def findEmployeeName(searchStr, get_doc=False):
    searchStr = searchStr.strip()

    name = frappe.db.exists("Employee", {"name": searchStr})
    if name:
        return name

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
