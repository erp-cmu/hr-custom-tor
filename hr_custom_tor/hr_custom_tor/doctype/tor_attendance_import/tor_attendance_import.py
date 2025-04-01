# Copyright (c) 2025, IECMU and contributors
# For license information, please see license.txt

import os
import re
import shutil

import frappe
from frappe.model.document import Document
from frappe.utils import get_site_path, now, getdate
import pandas as pd
from hr_custom_tor.services.hr import findEmployee
from hr_custom_tor.services.attendance import processCheckInDF


def insert_file_suffix_prefix(fname, suffix=None, prefix=None):
    if prefix is None:
        prefix = (
            now()[:19].replace("-", "_").replace(" ", "-").replace(":", "_")
        )  # i.e. 2025_03_15-11_30_32

    if suffix is None:
        suffix = ""

    if prefix:
        prefix = prefix + "_"

    if suffix:
        suffix = "_" + suffix

    f = fname.rsplit(".", 1)
    if len(f) == 1:
        partial, extn = f[0], ""
    else:
        partial, extn = f[0], "." + f[1]
    return f"{prefix}{partial}{suffix}{extn}"


def is_already_renamed(filepath):
    fname = os.path.basename(filepath)
    result = re.search(r"^\d{4}_\d{2}_\d{2}", fname)
    return bool(result)


class TorAttendanceImport(Document):
    def before_save(self):
        cur_filepath = self.checkin_file or None

        if cur_filepath and not is_already_renamed(cur_filepath):
            if not cur_filepath.startswith(("/private/files/", "/files/")):
                frappe.throw("File path is not valid")

            split = os.path.split(cur_filepath)
            # path_prefix with have leading "/" but not trailing "/"
            path_prefix, cur_filename = split
            # Add trailing "/" to align with the convention
            path_prefix = path_prefix + "/"

            try:
                cur_file_doc = frappe.get_last_doc(
                    "File",
                    filters={"file_url": cur_filepath},
                )
                if cur_file_doc:
                    new_filename = insert_file_suffix_prefix(cur_filename)
                    new_filepath = f"{path_prefix}{new_filename}"

                    site_path = get_site_path()  #'./SITENAME'
                    cur_filepath_site = f"{site_path}{cur_filepath}"  # The cur_filepath already contains leading "/""
                    new_filepath_site = f"{site_path}{new_filepath}"
                    shutil.copyfile(cur_filepath_site, new_filepath_site)
                    os.remove(cur_filepath_site)

                    cur_file_doc.file_url = new_filepath
                    cur_file_doc.file_name = new_filename
                    cur_file_doc.save()
                    self.checkin_file = cur_file_doc.file_url

                    # This method does not work
                    # new_file_doc = frappe.copy_doc(cur_file_doc)
                    # new_file_doc.is_private = cur_file_doc.is_private
                    # new_file_doc.file_url = new_filepath
                    # new_file_doc.file_name = new_filename
                    # new_file_doc.save(ignore_permissions=True)
                    # self.checkin_file = new_file_doc.file_url
                    # cur_file_doc.delete(ignore_permissions=True)
                else:
                    frappe.log_error("File not found.")
            except Exception as e:
                frappe.throw(
                    f"Error handling attachment: {str(e)}",
                    "Attachment Handling Exception",
                )

    def before_submit(self):
        inject_attendance(self)

    def start_import(self):
        try:
            progress(0, "Starting Import")
            import_from_checkin_file(self)
            self.status = "SUCCESS"
            progress(100, "Finish")
        except Exception:
            frappe.db.rollback()
            self.status = "PENDING"
        finally:
            pass
        return self


def import_from_checkin_file(doc):
    filepath = frappe.get_site_path() + doc.checkin_file
    if not os.path.exists(filepath):
        frappe.throw(title="Error", msg="This file does not exist")

    try:
        dfr = pd.read_excel(filepath)
    except Exception:
        frappe.throw(title="Error", msg="Cannot read excel file.")

    # Get Holiday
    thisYear = now()[:4]  # i.e. 2025
    holidays = frappe.get_all(
        "Holiday",
        filters={"parent": thisYear},
        fields=["holiday_date", "description"],
        as_list=True,
    )

    if len(holidays) == 0:
        frappe.throw(f"Cannot find holiday name {thisYear}")

    dfHoliday = pd.DataFrame.from_dict(holidays)
    dfHoliday.columns = ["date", "description"]
    dfHoliday["date"] = pd.to_datetime(dfHoliday["date"]).dt.strftime("%Y-%m-%d")
    dfHoliday = dfHoliday.sort_values(by="date", ascending=True).reset_index(drop=True)

    dfgm = processCheckInDF(dfr, dfHoliday)

    def createAttendanceItem(row):
        row = row.fillna(False)  # Default all to Faklse
        date = row["date"]
        employeeStr = row["name"]
        employee = findEmployee(employeeStr, get_doc=True)
        if not employee:
            frappe.throw(f"Cannot find employee for '{employeeStr}'")
        # if employee:
        #     fullname = frappe.db.get_value("Employee", employeeId, "employee_name") or ""
        item = frappe.get_doc(
            {
                "doctype": "Tor Attendance Import Item",
                "employee": employee.name,
                "fullname": employee.employee_name,
                "date": getdate(date, parse_day_first=True),
                "is_weekend": row["isWeekend"],
                "is_holiday": row["isHoliday"],
                "is_special_holiday": row["isSpecialHoliday"],
                "is_working_day": row["isWorkingDay"],
                "in": row["in"],
                "out": row["out"],
                "checkin_times": row["checkinTimes"],
            }
        )
        doc.append("attendance_data", item)
        pass

    filt = dfgm["markAttendance"]
    dfgm[filt].apply(createAttendanceItem, axis=1)

    pass


def inject_attendance(self):
    for attItem in self.attendance_data:
        employeeName = attItem.employee
        attDate = getdate(attItem.date)
        lateTime = 200

        # name = frappe.db.exists(
        #     "Attendance",
        #     {
        #         "employee": employeeName,
        #         "attendance_date": attDate,
        #     },
        # )
        # if name:
        #     frappe.db.set_value("Attendance", name, "custom_late_time", lateTime)
        # else:
        #     newAtt = frappe.get_doc(
        #         {
        #             "doctype": "Attendance",
        #             "employee": employeeName,
        #             "attendance_date": attDate,
        #             "custom_late_time": lateTime,
        #             "status": "Present",
        #             "docstatus": 1,
        #         }
        #     )
        #     newAtt.insert()


@frappe.whitelist()
def form_start_import(doc_name: str):
    return frappe.get_doc("Tor Attendance Import", doc_name).start_import()


def progress(prog: int, desc: str):
    frappe.publish_realtime(
        "data_import_progress", {"progress": prog, "description": desc}
    )
