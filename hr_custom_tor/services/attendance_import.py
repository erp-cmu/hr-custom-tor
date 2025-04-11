import numpy as np
import pandas as pd
from datetime import time, timedelta
from hr_custom_tor.services.date import getDateRange
import json


def processCheckInDF(dfr, dfHoliday):
    dfr = dfr.dropna(axis=0, how="all")

    # Change column name
    locDateCol = dfr.columns.get_loc("Date")
    timeColsOri = dfr.columns.values[locDateCol + 1 :]
    timeCols = [f"c{i}" for i in range(1, len(timeColsOri) + 1)]
    changeColNameDict = dict(zip(timeColsOri, timeCols))
    dfr = dfr.rename(columns={"ชื่อ-นามสกุล": "name", "Date": "date", **changeColNameDict})
    dfr = dfr[["name", "date", *timeCols]]

    # Remove duplicate
    dfr = dfr[~dfr.duplicated()]

    # Remove rows with all null
    filtNull = dfr[timeCols].isnull().all(axis=1)
    dfr = dfr[~filtNull]

    def parseDate(dateStr):
        sp = dateStr.split("/")
        day = sp[0]
        month = sp[1]
        year = int(sp[2]) - 543
        return pd.to_datetime(f"{year}/{month}/{day}", format="%Y/%m/%d")

    # Convert to datetime
    dfr["date"] = dfr["date"].apply(parseDate)

    # Convert to date
    dfr["date"] = dfr["date"].dt.date

    for col in timeCols:
        dfr[col] = pd.to_datetime(dfr[col], format="%H:%M").dt.time

    # Remove rows with hours outside acceptable range
    def checkTimeOutsideRange(sr):
        return (sr < time(hour=6)) | (sr > time(hour=22))

    filtOutsideRange = pd.Series(data=False, index=dfr.index)
    for col in timeCols:
        _filt = checkTimeOutsideRange(dfr[col])
        filtOutsideRange = filtOutsideRange | _filt
    dfr[filtOutsideRange]
    dfr = dfr[~filtOutsideRange]

    # Remove duplicates times
    def checkDuplicates(_sr):
        sr = _sr[~_sr.duplicated()]
        timeArr = sr.values
        timeArrPadded = [pd.NaT for i in range(len(timeCols))]
        for idx, val in enumerate(timeArr):
            timeArrPadded[idx] = val
        return pd.Series(timeArrPadded, index=timeCols)

    dfr[timeCols] = dfr[timeCols].apply(checkDuplicates, axis=1)

    # Check incomplete check-in/out
    dfr["incompleteInOut"] = False
    filtOneCheckIn = (~dfr[timeCols].isnull()).sum(axis=1) == 1
    dfr.loc[filtOneCheckIn, "incompleteInOut"] = True

    # Add time for incomplete check-in/out
    def addTimeForIncompleteCheckInOut(sr):
        dt_time = sr["c1"]
        # Determine whether the missing is the morning in or evening out.
        if dt_time < time(hour=12):  # 12pm
            sr["c2"] = time(hour=17)  # 5pm
        else:
            sr["c2"] = time(hour=8)  # 8am
        return sr

    filtIIO = dfr["incompleteInOut"]
    dfr.loc[filtIIO, :] = dfr.loc[filtIIO, :].apply(
        addTimeForIncompleteCheckInOut, axis=1
    )

    def calculateInOut(row):
        times = row.loc[timeCols].dropna()
        res = times.agg(["min", "max"])
        return pd.concat([row, res])

    dfr = dfr.apply(calculateInOut, axis=1)
    dfr = dfr.rename(columns={"min": "in", "max": "out"})
    dfr["isInLate"] = dfr["in"] > time(hour=8)
    dfr["isOutEarly"] = dfr["out"] < time(hour=17)

    # You cannot substract time and time. Need to convert to timedelta first.
    def calInLateMin(dt_time):
        deltaIn = timedelta(hours=dt_time.hour, minutes=dt_time.minute)
        deltaStart = timedelta(hours=8)
        lateMin = (deltaIn - deltaStart).total_seconds() / 60
        if lateMin < 0:
            lateMin = 0
        return lateMin

    dfr["inLateMin"] = dfr["in"].apply(calInLateMin)

    def calOutEarlyMin(dt_time):
        deltaOut = timedelta(hours=dt_time.hour, minutes=dt_time.minute)
        deltaEnd = timedelta(hours=17)
        earlyMon = (deltaEnd - deltaOut).total_seconds() / 60
        if earlyMon < 0:
            earlyMon = 0
        return earlyMon

    dfr["outEarlyMin"] = dfr["out"].apply(calOutEarlyMin)

    # Note: I will leave this logic for later since some company define late min differently.
    # Total late minutes
    # dfr["lateMin"] = dfr["inLateMin"] + dfr["outEarlyMin"]

    def calWorkingDuration(row):
        timeIn = row["in"]
        timeOut = row["out"]
        deltaIn = timedelta(hours=timeIn.hour, minutes=timeIn.minute)
        deltaOut = timedelta(hours=timeOut.hour, minutes=timeOut.minute)
        return (deltaOut - deltaIn).total_seconds() / 60

    dfr["workingDurationMin"] = dfr.apply(calWorkingDuration, axis=1)
    dfr["overworkMin"] = dfr["workingDurationMin"] - (9 * 60)

    # Holiday list
    # dfHoliday["date"] = pd.to_datetime(dfHoliday["date"])
    # dfHoliday["isHoliday"] = True
    # dfHoliday["isWeekend"] = dfHoliday["description"].str.contains(
    #     "Sunday|Saturday", regex=True
    # )
    # dfHoliday["isSpecialHoliday"] = ~dfHoliday["isWeekend"]
    # dfHoliday

    # Calculate working day
    workingDayStart = dfr["date"].min()
    workingDayEnd = dfr["date"].max()

    # Get working days range
    # dateRanges = pd.date_range(start=workingDayStart, end=workingDayEnd)
    # dfDateRangeTemp = pd.DataFrame(data={"date": dateRanges})
    # dfDateRangeTemp.head()

    # # Determine holidays
    # dfDateRange = dfDateRangeTemp.merge(dfHoliday, on="date", how="left")
    # dfDateRange["description"] = dfDateRange["description"].fillna("")
    # dfDateRange[["isWeekend", "isHoliday", "isSpecialHoliday"]] = dfDateRange[
    #     ["isWeekend", "isHoliday", "isSpecialHoliday"]
    # ].fillna(False)
    
    # dfDateRange["isWorkingDay"] = ~dfDateRange["isHoliday"]

    # # Convert datetime to date so that I can merge.
    # dfDateRange["date"] = dfDateRange["date"].dt.date
    
    dfDateRange = getDateRange(dayStart=workingDayStart, dayEnd=workingDayEnd, dfHoliday=dfHoliday)

    # Merging
    def matchDateRange(_dft):
        dft = _dft.copy()
        dft["checkPresent"] = 1
        dfm = pd.merge(
            dfDateRange,
            dft,
            left_on="date",
            right_on="date",
            how="left",
            suffixes=("", "_y"),
        )
        dfm["isPresent"] = dfm["checkPresent"].notnull()
        dfm["isAbsent"] = dfm["checkPresent"].isnull()
        return dfm

    dfg = dfr.groupby(by="name")
    dfgm = dfg.apply(matchDateRange, include_groups=False)
    dfgm = dfgm.drop(columns=["checkPresent"])
    dfgm = dfgm.reset_index().drop(columns="level_1")

    def determine_is_present_on_working_day(sr):
        isWorkingDay = sr["isWorkingDay"]
        if not isWorkingDay:
            return np.nan
        isPresent = sr["isPresent"]
        if isPresent:
            return True
        else:
            return False

    dfgm["isPresentOnWorkingDay"] = dfgm.apply(
        determine_is_present_on_working_day, axis=1
    )

    def determine_is_absent_on_working_day(sr):
        isWorkingDay = sr["isWorkingDay"]
        if not isWorkingDay:
            return np.nan
        isPresent = sr["isPresent"]
        if isPresent:
            return False
        else:
            return True

    dfgm["isAbsentOnWorkingDay"] = dfgm.apply(
        determine_is_absent_on_working_day, axis=1
    )

    def determine_is_present_on_holiday_and_weekend(sr):
        isWorkingDay = sr["isWorkingDay"]
        if isWorkingDay:
            return np.nan
        isPresent = sr["isPresent"]
        if isPresent:
            return True
        else:
            return False

    dfgm["isPresentOnHolidayWeekend"] = dfgm.apply(
        determine_is_present_on_holiday_and_weekend, axis=1
    )

    # Determine if I should mark attendance in ERPNext or not
    def determineMarkAttendance(row):
        if not row["isHoliday"]:
            return True
        else:
            if row["isPresent"]:
                return True
            else:
                return False

    dfgm["markAttendance"] = dfgm.apply(determineMarkAttendance, axis=1)

    # Combine checkin times into single array
    def makeCheckinArray(_sr):
        sr = _sr.dropna()
        sr = sr.apply(lambda x: x.strftime("%H:%M:%S"))
        return json.dumps(sr.values.tolist())

    dfgm["checkinTimes"] = dfgm[timeCols].apply(makeCheckinArray, axis=1)

    return dfgm
