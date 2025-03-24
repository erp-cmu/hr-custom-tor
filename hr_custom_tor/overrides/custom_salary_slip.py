import frappe

# from frappe.utils.nestedset import NestedSet
from erpnext.controllers.status_updater import validate_status
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
import requests


class CustomSalarySlip(SalarySlip):
    def validate(self):
        super().validate()
        self.my_custom_code()

    def my_custom_code(self):
        frappe.msgprint("Hello")

    @frappe.whitelist()
    def get_emp_and_working_day_details(self):
        super().get_emp_and_working_day_details()

        # r = requests.post(
        #     "http://localhost:8000/api/method/calc_salary", json={"name": "nirand"}
        # )

        # frappe.msgprint(r.json())

        # try:
        # Function definition
        # def script_calculate_salary(self):
        #     return None

        lc = {}
        sc = frappe.get_doc("Server Script", "Calculate Salary")
        exec(sc.script, locals(), lc)

        amount = lc["amount"]

        # amount = script_calculate_salary(self)
        # amount = calc_amount()
        frappe.msgprint(str(amount))
        # except Exception:
        #     frappe.throw("Error executing server script")

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
