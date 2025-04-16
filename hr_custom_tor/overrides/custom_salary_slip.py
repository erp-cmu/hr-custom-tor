import frappe

# from frappe.utils.nestedset import NestedSet
from erpnext.controllers.status_updater import validate_status
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hr_custom_tor.services.attendance_analyze import (
    getDateRange,
    getDfAttSummary,
    getDfHoliday,
    getDfAtt,
)
import datetime


class CustomSalarySlip(SalarySlip):
    def validate(self):
        super().validate()
        self.my_custom_code()

    def my_custom_code(self):
        frappe.msgprint("Hello")

    @frappe.whitelist()
    def get_emp_and_working_day_details(self):
        super().get_emp_and_working_day_details()

        ############################
        # Another way to get information from server script (not using this right now)
        ############################
        # try:
        #     lc = {}
        #     sc = frappe.get_doc("Server Script", "Calculate Salary")
        #     exec(sc.script, locals(), lc)
        #     amount = lc["amount"]
        #     frappe.msgprint(str(amount))
        # except Exception:
        #     frappe.throw("Error executing server script")

        startDate = self.start_date
        endDate = self.end_date

        if (startDate is None) or (endDate is None):
            return
            # frappe.throw("No start_date or end_date")

        if isinstance(startDate, str):
            startDateStr = startDate
            endDateStr = endDate
        elif isinstance(startDate, datetime.date):
            startDateStr = startDate.strftime("%Y-%m-%d")
            endDateStr = endDate.strftime("%Y-%m-%d")

        employeeNames = [self.employee]

        dfAtt, dfDateRange = getDfAtt(
            startDate=startDateStr, endDate=endDateStr, employeeNames=employeeNames
        )

        sd = frappe.get_doc(
            {
                "doctype": "Salary Detail",
                "salary_component": "Deduction",
                "amount": 1000,
                "parent": self,
                "parenttype": "Salary Slip",
            }
        )

        self.append("deductions", sd)
        self.calculate_net_pay()
        frappe.msgprint("Hello")
