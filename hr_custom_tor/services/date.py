import frappe
import pandas as pd


def getDfHoliday(holidayListName):
    holidays = frappe.get_all(
        "Holiday",
        filters={"parent": holidayListName},
        fields=["holiday_date", "description"],
        as_list=False,
    )
    if len(holidays) == 0:
        frappe.throw(f"Cannot find holiday. Please make a holiday name: {holidayListName}.")
    # Need to convert frappe._dict to ordinary dict
    holidaysDict = [dict(h) for h in holidays]
    dfHoliday = pd.DataFrame.from_dict(holidaysDict)
    dfHoliday = dfHoliday.rename(columns={"holiday_date": "date"})
    dfHoliday["date"] = pd.to_datetime(dfHoliday["date"])
    dfHoliday = dfHoliday.sort_values(by="date", ascending=True).reset_index(drop=True)
    dfHoliday["isHoliday"] = True
    dfHoliday["isWeekend"] = dfHoliday["description"].str.contains(
        "Sunday|Saturday", regex=True
    )
    dfHoliday["isSpecialHoliday"] = ~dfHoliday["isWeekend"]
    return dfHoliday


def getDateRange(dayStart, dayEnd, dfHoliday, changeBoolToInt=False):
    # Calculate working day
    workingDayStart = dayStart
    workingDayEnd = dayEnd

    # Get working days range
    dateRanges = pd.date_range(start=workingDayStart, end=workingDayEnd)
    dfDateRangeTemp = pd.DataFrame(data={"date": dateRanges})

    # Determine holidays
    dfDateRange = dfDateRangeTemp.merge(dfHoliday, on="date", how="left")
    dfDateRange["description"] = dfDateRange["description"].fillna("")
    dfDateRange[["isWeekend", "isHoliday", "isSpecialHoliday"]] = dfDateRange[
        ["isWeekend", "isHoliday", "isSpecialHoliday"]
    ].fillna(False)
    dfDateRange["isWorkingDay"] = ~dfDateRange["isHoliday"]

    # Convert datetime to date so that I can merge.
    dfDateRange["date"] = dfDateRange["date"].dt.date
    
    if changeBoolToInt:
        dfDateRange = dfDateRange.replace({
            False: 0,
            True: 1
        })
    return dfDateRange
