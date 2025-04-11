import frappe
import pandas as pd
import json
import numpy as np
from hr_custom_tor.services.date import getDfHoliday, getDateRange

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


def getDfAtt(startDate: str, endDate: str, employeeNames: list[str]):
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
        return None

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
    dfAtt[cols] = dfAtt.apply(
        lambda row: refillMissingDateDetails(row, dfDateRange), axis=1
    )

    # Add additional value filling as needed here
    colsNum = ["in_late_min", "out_early_min", "custom_leave_hours"]
    dfAtt[colsNum] = dfAtt[colsNum].fillna(0)

    dfAtt["is_on_leave"] = dfAtt["status"].apply(
        lambda s: 1 if s in ["Half Day", "On Leave"] else 0
    )

    dfAtt["late_min"] = dfAtt[
        "in_late_min"
    ]  # Note that some company might includes out_early_min
    dfAtt["late_min_effective"] = dfAtt["late_min"] - dfAtt["custom_leave_hours"] * 60

    def calculate_late_penalty(row):
        late_min = row["late_min_effective"]
        late_major_penalty_count = 0
        late_minor_penalty_min = 0
        if late_min > 10:
            late_major_penalty_count = 1
        else:
            late_minor_penalty_min = late_min
        return pd.Series(
            [late_major_penalty_count, late_minor_penalty_min],
            index=["late_major_penalty_count", "late_minor_penalty_min"],
        )

    dfAtt[["late_major_penalty_count", "late_minor_penalty_min"]] = dfAtt.apply(
        calculate_late_penalty, axis=1
    )

    # dfAtt = dfAtt.fillna(np.nan).replace([np.nan], [None])
    dfAtt = dfAtt.fillna(0)

    dfAtt = dfAtt.sort_values(
        by=["employee_name", "attendance_date"], ascending=[True, True]
    )
    return dfAtt


def getDfAttSummary(dfAtt):
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
                "is_on_leave": "sum",
                "late_major_penalty_count": "sum",
                "late_minor_penalty_min": lambda s: s.sum() if s.sum() > 0 else 0,
            }
        )
        .reset_index()
    )

    dfAttSummary["late_major_penalty_daily_pay_ratio"] = dfAttSummary[
        "late_major_penalty_count"
    ].apply(lambda s: s / 3 if s > 3 else 0)

    dfAttSummary["late_minor_penalty_daily_pay_ratio"] = dfAttSummary[
        "late_minor_penalty_min"
    ].apply(lambda s: s / 60 if s > 60 else 0)

    dfAttSummary["late_minor_penalty_thb"] = dfAttSummary[
        "late_minor_penalty_min"
    ].apply(lambda s: s if s <= 60 else 0)

    # Inject "employee_name" so that the "employee" (i.e. EMP-001) columns has "employee_name" (i.e. พี่หนอ) on it. (Something in frappe that makes this happen.)
    dfAttSummary["employee_name"] = dfAttSummary["employee"].apply(
        lambda emp: dfAtt[dfAtt["employee"] == emp]["employee_name"].values[0]
    )
    dfAttSummary = dfAttSummary.round(2)

    return dfAttSummary
