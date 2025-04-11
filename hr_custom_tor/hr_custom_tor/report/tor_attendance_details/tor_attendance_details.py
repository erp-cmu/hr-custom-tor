# Copyright (c) 2025, IECMU and contributors
# For license information, please see license.txt

import frappe

# import pandas as pd
# import numpy as np
from hr_custom_tor.services.attendance_analyze import getDfAtt, getDfAttSummary


def execute(filters=None):
    frappe.errprint(filters)

    startDate = filters["start_date"]
    endDate = filters["end_date"]
    employeeNames = filters["employee_names"]
    isSummary = bool(filters.get("is_summary"))

    ############################
    # Attendance information
    ############################
    dfAtt = getDfAtt(startDate=startDate, endDate=endDate, employeeNames=employeeNames)

    ############################
    # Create columns to display
    ############################
    columnsBase = [
        {
            "fieldname": "employee",
            "label": "พนักงาน",
            "fieldtype": "Link",
            "options": "Employee",
            "hidden": 0,
            "width": 250,
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
            "label": "(status)",
            "fieldtype": "Data",
        },
        {
            "fieldname": "is_working_day",
            "label": "วันทำงาน",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_on_leave",
            "label": "วันลา",
            "fieldtype": "Check" if not isSummary else "Int",
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
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_in_late",
            "label": "เข้างานสาย",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_out_early",
            "label": "ออกงานเร็ว",
            "fieldtype": "Check" if not isSummary else "Int",
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
            "fieldname": "late_min_effective",
            "label": "เวลาสายรวมการลา (นาที)",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_major_penalty_count",
            "label": "late_major_penalty_count",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_minor_penalty_min",
            "label": "late_minor_penalty_min",
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
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_absent",
            "label": "is_absent",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_weekend",
            "label": "is_weekend",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_holiday",
            "label": "is_holiday",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_special_holiday",
            "label": "is_special_holiday",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_present_on_working_day",
            "label": "is_present_on_working_day",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_absent_on_working_day",
            "label": "is_absent_on_working_day",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_present_on_holiday_weekend",
            "label": "is_present_on_holiday_weekend",
            "fieldtype": "Check" if not isSummary else "Int",
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

    colsBaseToSummary = [
        "employee",
        "is_present",
        "is_absent",
        "is_working_day",
        "is_present_on_working_day",
        "is_present_on_holiday_weekend",
        "working_duration_min",
        "overwork_min",
        "incomplete_in_out",
        "in_late_min",
        "out_early_min",
        "late_min",
        "late_min_effective",
        "is_on_leave",
        "custom_leave_hours",
        "late_major_penalty_count",
        "late_minor_penalty_min",
        {
            "fieldname": "late_major_penalty_daily_pay_ratio",
            "label": "late_major_penalty_daily_pay_ratio",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_minor_penalty_daily_pay_ratio",
            "label": "late_minor_penalty_daily_pay_ratio",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_minor_penalty_thb",
            "label": "late_minor_penalty_thb",
            "fieldtype": "Float",
        },
    ]
    columnsSummary = []
    for fieldnameQuery in colsBaseToSummary:
        if isinstance(fieldnameQuery, str):
            res = [c for c in columnsBase if c.get("fieldname") == fieldnameQuery]
            columnsSummary.append(res[0])
        else:
            columnsSummary.append(fieldnameQuery)

    if not isSummary:
        columns = columnsBase
    else:
        columns = columnsSummary

    ############################
    # Output
    ############################
    # If no attendance is found, return blank data
    if dfAtt is None:
        return columns, []

    if not isSummary:
        data = dfAtt.to_dict(orient="records")
    else:
        dfAttSummary = getDfAttSummary(dfAtt=dfAtt)
        data = dfAttSummary.to_dict(orient="records")

    return columns, data
