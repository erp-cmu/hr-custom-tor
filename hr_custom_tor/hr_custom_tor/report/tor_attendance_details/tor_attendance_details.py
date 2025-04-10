# Copyright (c) 2025, IECMU and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_site_path, now, getdate
import pandas as pd
import json
import numpy as np
from hr_custom_tor.services.date import getDfHoliday, getDateRange

colsJson = [
    "checkin_times",
    "date",
    "description",
    "employee",
    "fullname",
    "idx",
    "in",
    "in_late_min",
    "incomplete_in_out",
    "is_absent",
    "is_absent_on_working_day",
    "is_holiday",
    "is_in_late",
    "is_out_early",
    "is_present",
    "is_present_on_holiday_weekend",
    "is_present_on_working_day",
    "is_special_holiday",
    "is_weekend",
    "is_working_day",
    "late_min",
    "mark_attendance",
    "out",
    "out_early_min",
    "overwork_min",
    "working_duration_min",
]

# Blank data in case the attendance item does not have json.
blankDict = {
    "__unsaved": 1,
    "checkin_times": [],
    "creation": "",
    "date": "",
    "description": "",
    "docstatus": 1,
    "doctype": "Tor Attendance Import Item",
    "employee": "",
    "fullname": "",
    "idx": -1,
    "in": "",
    "in_late_min": 0.0,
    "incomplete_in_out": 0,
    "is_absent": 0,
    "is_absent_on_working_day": 0,
    "is_holiday": np.nan,
    "is_in_late": 0,
    "is_out_early": 0,
    "is_present": 0,
    "is_present_on_holiday_weekend": 0,
    "is_present_on_working_day": 0,
    "is_special_holiday": np.nan,
    "is_weekend": np.nan,
    "is_working_day": np.nan,
    "late_min": 0.0,
    "mark_attendance": 0,
    "modified": "",
    "modified_by": "",
    "name": "",
    "naming_series": "",
    "out": "",
    "out_early_min": 0.0,
    "overwork_min": 0.0,
    "owner": "",
    "parent": "",
    "parentfield": "",
    "parenttype": "",
    "working_duration_min": 0.0,
}


def execute(filters=None):
    frappe.errprint(filters)

    startDate = filters["start_date"]
    endDate = filters["end_date"]
    employeeNames = filters["employee_names"]
    isSummary = bool(filters.get("is_summary"))

    columnsDetails = [
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

    colsToReuse = [
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
    ]
    columnsSummary = []
    for fieldnameQuery in colsToReuse:
        res = [c for c in columnsDetails if c.get("fieldname") == fieldnameQuery]
        columnsSummary.append(res[0])

    if not isSummary:
        columns = columnsDetails
    else:
        columns = columnsSummary

    filterAtt = {
        "attendance_date": ["between", [startDate, endDate]],
        "docstatus": 1,
    }

    if len(employeeNames) > 0:
        filterAtt["employee"] = ["in", employeeNames]

    atts = frappe.db.get_all(
        "Attendance",
        filters=filterAtt,
        fields=["*"],
    )
    attsDict = [dict(att) for att in atts]
    
    # If no attendance is found, exit
    if len(attsDict) == 0:
        return columns, []
    
    _dfAtt = pd.DataFrame.from_dict(attsDict)
    dfJson = _dfAtt["custom_import_details"].apply(
        lambda x: json.loads(x) if x is not None else blankDict
    )
    _dfAttDetails = pd.DataFrame.from_dict(dfJson.values.tolist())
    _dfAttDetails.index = dfJson.index
    dfAtt = pd.concat([_dfAtt, _dfAttDetails], axis=1)
    # There are dupliated columns. Remove.
    dfAtt = dfAtt.loc[:, ~dfAtt.columns.duplicated()].copy()

    # Takes care of date details.
    holidayListName = startDate[:4]
    dfHoliday = getDfHoliday(holidayListName=holidayListName)
    dfDateRange = getDateRange(
        dayStart=pd.to_datetime(startDate).date(),
        dayEnd=pd.to_datetime(endDate).date(),
        dfHoliday=dfHoliday,
        changeBoolToInt=True,
    )

    def refillMissingDateDetails(row, dfDateRange):
        cols = ["isHoliday", "isWeekend", "isSpecialHoliday", "isWorkingDay"]
        _date = row["attendance_date"]        
        filt = dfDateRange["date"] == _date
        dfDateRangeFilt = dfDateRange[filt]
        if dfDateRangeFilt.shape[0] != 1:
            frappe.throw("Cannot find date range for this date")
        sr = pd.Series((dfDateRangeFilt[cols].to_dict(orient="records"))[0])
        return sr
    
    cols = ["is_holiday", "is_weekend", "is_special_holiday", "is_working_day"]
    dfAtt[cols] = dfAtt.apply(lambda row: refillMissingDateDetails(row, dfDateRange), axis=1)

    colsNum = ["late_min", "custom_leave_hours"]
    dfAtt[colsNum] = dfAtt[colsNum].fillna(0)

    dfAtt["is_on_leave"] = dfAtt["status"].apply(
        lambda s: True if s in ["Half Day", "On Leave"] else False
    )

    dfAtt["late_min_effective"] = dfAtt["late_min"] - dfAtt["custom_leave_hours"] * 60

    # Change NaN to None just to make sure.
    dfAtt = dfAtt.fillna(np.nan).replace([np.nan], [None])

    dfAtt = dfAtt.sort_values(
        by=["employee_name", "attendance_date"], ascending=[True, True]
    )

    colsDF = [
        "employee",
        "employee_name",
        "attendance_date",
        "description",
        "status",
        "is_working_day",
        "is_on_leave",
        "custom_leave_hours",
        "in",
        "out",
        "incomplete_in_out",
        "is_in_late",
        "is_out_early",
        "in_late_min",
        "out_early_min",
        "late_min",
        "late_min_effective",
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

    dfAttSummary = (
        dfAtt.groupby(by=["employee"])
        .agg(
            {
                "is_present": "sum",
                "is_absent": "sum",
                "is_working_day": "sum",
                "is_present_on_working_day": "sum",
                "is_present_on_holiday_weekend": "sum",
                "working_duration_min": lambda s: s.mean(),
                "overwork_min": "sum",
                "incomplete_in_out": "sum",
                "in_late_min": "sum",
                "out_early_min": "sum",
                "late_min": "sum",
                "custom_leave_hours": "sum",
                "late_min_effective": "sum",
            }
        )
        .reset_index()
    )
    # Inject "employee_name" so that the "employee" (i.e. EMP-001) columns has "employee_name" (i.e. พี่หนอ) on it. (Something in frappe that makes this happen.)
    dfAttSummary["employee_name"] = dfAttSummary["employee"].apply(
        lambda emp: dfAtt[dfAtt["employee"] == emp]["employee_name"].values[0]
    )
    dfAttSummary = dfAttSummary.round(2)

    if not isSummary:
        data = dfAtt[colsDF].to_dict(orient="records")
    else:
        data = dfAttSummary.to_dict(orient="records")

    return columns, data
