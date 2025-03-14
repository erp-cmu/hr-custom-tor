import frappe

# from frappe.utils.nestedset import NestedSet
from erpnext.controllers.status_updater import validate_status
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip


class CustomSalarySlip(SalarySlip):
    def validate(self):
        super().validate()
        self.my_custom_code()

    def my_custom_code(self):
        frappe.msgprint("Hello")

    @frappe.whitelist()
    def get_emp_and_working_day_details(self):
        super().get_emp_and_working_day_details()

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
