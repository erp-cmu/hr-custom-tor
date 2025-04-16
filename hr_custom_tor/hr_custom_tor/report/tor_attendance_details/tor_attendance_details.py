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
    isDev = bool(filters.get("is_dev"))

    ############################
    # Attendance information
    ############################
    dfAtt, dfDateRange = getDfAtt(
        startDate=startDate, endDate=endDate, employeeNames=employeeNames
    )

    ############################
    # Create columns to display
    ############################
    colsBase = [
        {
            "fieldname": "employee",
            "label": "รหัสพนักงาน" if not isDev else "employee",
            # "fieldtype": "Link",
            "fieldtype": "Data",
            "options": "Employee",
            "hidden": 0,
            # "width": 250,
        },
        {
            "fieldname": "employee_name",
            "label": "ชื่อ" if not isDev else "employee",
            "fieldtype": "Data",
            "hidden": 0,
            # "width": 250,
        },
        {
            "fieldname": "attendance_date",
            "label": "วันที่" if not isDev else "attendance_date",
            "fieldtype": "Data",
        },
        {
            "fieldname": "description",
            "label": "วันพิเศษ" if not isDev else "description",
            "fieldtype": "Data",
        },
        {
            "fieldname": "status",
            "label": "สถานะเข้างาน" if not isDev else "status",
            "fieldtype": "Data",
        },
        {
            "fieldname": "is_working_day",
            "label": "วันทำงาน" if not isDev else "is_working_day",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_on_leave",
            "label": "ลาเต็มวัน" if not isDev else "is_on_leave",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_on_partial_leave",
            "label": "ลาไม่เต็มวัน" if not isDev else "is_on_partial_leave",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "custom_leave_hours",
            "label": "ชั่วโมงลา" if not isDev else "custom_leave_hours",
            "fieldtype": "Int",
        },
        {
            "fieldname": "in",
            "label": "เวลาเข้างาน" if not isDev else "in",
            "fieldtype": "Time",
        },
        {
            "fieldname": "out",
            "label": "เวลาออกงาน" if not isDev else "out",
            "fieldtype": "Time",
        },
        {
            "fieldname": "incomplete_in_out",
            "label": "เช็คชื่อไม่ครบ" if not isDev else "incomplete_in_out",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_in_late",
            "label": "เข้างานสาย" if not isDev else "is_in_late",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_out_early",
            "label": "ออกงานเร็ว" if not isDev else "is_out_early",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "in_late_min",
            "label": "เวลาเข้างานสาย (นาที)" if not isDev else "in_late_min",
            "fieldtype": "Float",
        },
        {
            "fieldname": "out_early_min",
            "label": "เวลาออกงานเร็ว (นาที)" if not isDev else "out_early_min",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_min",
            "label": "เวลาสาย (นาที)" if not isDev else "late_min",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_min_effective",
            "label": "เวลาสายรวมการลา (นาที)" if not isDev else "late_min_effective",
            "fieldtype": "Float",
        },
        {
            "fieldname": "late_over_10min_count",
            "label": "มาสายเกิน 10 นาที (ครั้ง)" if not isDev else "late_over_10min_count",
            "fieldtype": "Int",
        },
        {
            "fieldname": "late_min_for_deduct",
            "label": "เข้างานเกินเวลา (หัก 1 บาท)" if not isDev else "late_min_for_deduct",
            "fieldtype": "Float",
        },
        {
            "fieldname": "working_duration_min",
            "label": "เวลาทำงาน (นาที)" if not isDev else "working_duration_min",
            "fieldtype": "Data",
        },
        {
            "fieldname": "overwork_min",
            "label": "ทำเกิน (นาที)" if not isDev else "overwork_min",
            "fieldtype": "Data",
        },
        {
            "fieldname": "is_present",
            "label": "เข้างาน" if not isDev else "is_present",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_absent",
            "label": "ขาดงาน" if not isDev else "is_absent",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_weekend",
            "label": "วันหยุดที่เป็นอาทิตย์" if not isDev else "is_weekend",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_holiday",
            "label": "วันหยุด" if not isDev else "is_holiday",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_special_holiday",
            "label": "วันหยุดพิเศษ" if not isDev else "is_special_holiday",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_present_on_working_day",
            "label": "เข้างานในวันทำงาน" if not isDev else "is_present_on_working_day",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_absent_on_working_day",
            "label": "ขาดงานในวันทำงาน" if not isDev else "is_absent_on_working_day",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "is_present_on_holiday_weekend",
            "label": "เข้างานในวันหยุด" if not isDev else "is_present_on_holiday_weekend",
            "fieldtype": "Check" if not isSummary else "Int",
        },
        {
            "fieldname": "custom_import_reference",
            "label": "Import Ref" if not isDev else "Import Ref",
            "fieldtype": "Link",
            "options": "Tor Attendance Import",
        },
        {
            "fieldname": "custom_reference_item_index",
            "label": "Import Ref Idx" if not isDev else "custom_reference_item_index",
            "fieldtype": "Int",
        },
        {
            "fieldname": "deduct_ngan_late",
            "label": "จำนวนหักงาน (มาสาย)" if not isDev else "deduct_ngan",
            "fieldtype": "Int",
        },
        {
            "fieldname": "deduct_ngan_absent",
            "label": "จำนวนวันทำงานไม่ครบ" if not isDev else "deduct_ngan_absent",
            "fieldtype": "Int",
        },
    ]

    colsFieldDaily = [
        "employee",
        "employee_name",
        "attendance_date",
        "is_working_day",
        "description",
        "status",
        "is_present",
        "is_absent",
        "is_on_leave",
        "is_on_partial_leave",
        "is_present_on_working_day",
        "custom_leave_hours",
        "late_min",
        "late_min_effective",
        "late_over_10min_count",
        "late_min_for_deduct",
        "in",
        "out",
        "incomplete_in_out",
        "is_in_late",
        "is_out_early",
        "in_late_min",
        "out_early_min",
        "working_duration_min",
        "overwork_min",
        "is_weekend",
        "is_holiday",
        "is_special_holiday",
        "is_absent_on_working_day",
        "is_present_on_holiday_weekend",
        "custom_import_reference",
        "custom_reference_item_index",
    ]

    colsFieldSummary = [
        "employee",
        "employee_name",
        "is_working_day",
        "is_present",
        "is_absent",
        "is_on_leave",
        "deduct_ngan_absent",
        "is_on_partial_leave",
        "is_present_on_working_day",
        "is_present_on_holiday_weekend",
        "late_min_effective",
        "late_over_10min_count",
        "late_min_for_deduct",
        "deduct_ngan_late",
        "late_min",
        "working_duration_min",
        "overwork_min",
        "incomplete_in_out",
        "in_late_min",
        "out_early_min",
        "custom_leave_hours",
    ]

    colsFields = colsFieldDaily if not isSummary else colsFieldSummary
    columns = []
    for fieldnameQuery in colsFields:
        res = [c for c in colsBase if c.get("fieldname") == fieldnameQuery]
        columns.append(res[0])

    ############################
    # Output
    ############################
    # If no attendance is found, return blank data
    if dfAtt is None:
        return columns, []

    if not isSummary:
        data = dfAtt.to_dict(orient="records")
    else:
        dfAttSummary = getDfAttSummary(dfAtt=dfAtt, dfDateRange=dfDateRange)
        data = dfAttSummary.to_dict(orient="records")

    return columns, data
