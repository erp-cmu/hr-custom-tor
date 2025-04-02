# Copyright (c) 2025, IECMU and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_site_path, now, getdate
import pandas as pd
import json


def execute(filters=None):
    frappe.errprint(filters)
    columns = [
        {
            "fieldname": "employee",
            "label": "พนักงาน",
            "fieldtype": "Link",
            "options": "Employee",
            "hidden": 0,
            # "width": 300,
        },
        {
            "fieldname": "attendance_date",
            "label": "วันที่",
            "fieldtype": "Data",
        },
        {
            "fieldname": "description",
            "label": "วันพิเศษ",
            "fieldtype": "Data",
        },
        {
            "fieldname": "status",
            "label": "status",
            "fieldtype": "Data",
        },
        {
            "fieldname": "is_working_day",
            "label": "เป็นวันทำงาน",
            "fieldtype": "Check",
        },
        {
            "fieldname": "custom_leave_hours",
            "label": "ชั่วโมงลา",
            "fieldtype": "Int",
        },
        {
            "fieldname": "in",
            "label": "เวลาเข้างาน",
            "fieldtype": "Time",
        },
        {
            "fieldname": "out",
            "label": "เวลาออกงาน",
            "fieldtype": "Time",
        },
        {
            "fieldname": "incomplete_in_out",
            "label": "เช็คชื่อไม่ครบ",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_in_late",
            "label": "เข้างานสาย",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_out_early",
            "label": "ออกงานเร็ว",
            "fieldtype": "Check",
        },
        {
            "fieldname": "in_late_min",
            "label": "เวลาเข้างานสาย (นาที)",
            "fieldtype": "Float",
        },
        {
            "fieldname": "out_early_min",
            "label": "เวลาออกงานเร็ว (นาที)",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_min",
            "label": "เวลาสาย (นาที)",
            "fieldtype": "Float",
        },
        {
            "fieldname": "working_duration_min",
            "label": "เวลาทำงาน (นาที)",
            "fieldtype": "Data",
        },
        {
            "fieldname": "overwork_min",
            "label": "ทำเกิน (นาที)",
            "fieldtype": "Data",
        },
        {
            "fieldname": "is_present",
            "label": "is_present",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_absent",
            "label": "is_absent",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_weekend",
            "label": "is_weekend",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_holiday",
            "label": "is_holiday",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_special_holiday",
            "label": "is_holiday",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_present_on_working_day",
            "label": "is_present_on_working_day",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_absent_on_working_day",
            "label": "is_absent_on_working_day",
            "fieldtype": "Check",
        },
        {
            "fieldname": "is_present_on_holiday_weekend",
            "label": "is_present_on_holiday_weekend",
            "fieldtype": "Check",
        },
        {
            "fieldname": "custom_import_reference",
            "label": "Import Ref",
            "fieldtype": "Link",
            "options": "Tor Attendance Import",
        },
        {
            "fieldname": "custom_reference_item_index",
            "label": "Import Ref Idx",
            "fieldtype": "Int",
        },
    ]

    startDate = filters["start_date"]
    endDate = filters["end_date"]

    atts = frappe.db.get_all(
        "Attendance",
        filters={"attendance_date": ["between", [startDate, endDate]], "docstatus": 1},
        fields=["*"],
    )
    attsDict = [dict(att) for att in atts]
    _dfAtt = pd.DataFrame.from_dict(attsDict)
    dfJson = _dfAtt["custom_import_details"].apply(lambda x: json.loads(x))
    _dfAttDetails = pd.DataFrame.from_dict(dfJson.values.tolist())
    _dfAttDetails.index = dfJson.index
    dfAtt = pd.concat([_dfAtt, _dfAttDetails], axis=1)

    cols = [
        "employee",
        "employee_name",
        "attendance_date",
        "description",
        "status",
        "is_working_day",
        "custom_leave_hours",
        "in",
        "out",
        "incomplete_in_out",
        "is_in_late",
        "is_out_early",
        "in_late_min",
        "out_early_min",
        "late_min",
        "working_duration_min",
        "overwork_min",
        "is_present",
        "is_absent",
        "is_weekend",
        "is_holiday",
        "is_special_holiday",
        "is_present_on_working_day",
        "is_absent_on_working_day",
        "is_present_on_holiday_weekend",
        "custom_import_reference",
        "custom_reference_item_index",
    ]
    data = dfAtt[cols].to_dict(orient="records")

    return columns, data
