import frappe

# from frappe.utils.nestedset import NestedSet
from erpnext.controllers.status_updater import validate_status
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hr_custom_tor.services.attendance_analyze import (
    getDfAtt,
    getDfAttSummary,
)
import datetime
from frappe.utils import (
    cint,
    cstr,
    flt,
    rounded,
)


def getSalaryDetails(parent, abbr):
    if (not parent.get("earnings")) or (not parent.get("deductions")):
        frappe.thorw("No earnings or deductions attributes found")
    earnings = parent.earnings
    deductions = parent.deductions
    salaryDetailArr = [*earnings, *deductions]
    resArr = [sd for sd in salaryDetailArr if sd.abbr == abbr]
    if len(resArr) == 0:
        frappe.throw(
            f"No Salary Component with abbreviation {abbr}. Please create one."
        )
    if len(resArr) > 1:
        frappe.throw(f"Found duplicated abbreviations in salary components {abbr}")
    return resArr[0]


class CustomSalarySlip(SalarySlip):
    def validate(self):
        super().validate()
        self.my_custom_code()

    def my_custom_code(self):
        frappe.msgprint("Hello")

    def getAmountFromSalaryStructure(self, abbr):
        doc = getSalaryDetails(parent=self._salary_structure_doc, abbr=abbr)
        return doc.amount

    def updateSalaryDetails(self, abbr, updatedAmount):
        # For some reasons, I need to update the salary details in two places or else the value will be reverted after recalculated the total amount.
        ssA = getSalaryDetails(parent=self, abbr=abbr)
        ssB = getSalaryDetails(parent=self._salary_structure_doc, abbr=abbr)
        ssA.amount = updatedAmount
        ssB.amount = updatedAmount

    @frappe.whitelist()
    def get_emp_and_working_day_details(self):
        super().get_emp_and_working_day_details()

        ####################################################################################
        # Another way to get information from server script (not using this right now)
        ####################################################################################
        # try:
        #     lc = {}
        #     sc = frappe.get_doc("Server Script", "Calculate Salary")
        #     exec(sc.script, locals(), lc)
        #     amount = lc["amount"]
        #     frappe.msgprint(str(amount))
        # except Exception:
        #     frappe.throw("Error executing server script")
        ####################################################################################

        startDate = self.start_date
        endDate = self.end_date

        if (startDate is None) or (endDate is None):
            # frappe.throw("No start_date or end_date")
            return

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
        if dfAtt is None:
            frappe.msgprint("No attendance found.")
            return
        dfAttSummary = getDfAttSummary(dfAtt=dfAtt, dfDateRange=dfDateRange)
        srAttSummary = dfAttSummary.iloc[0, :]

        baseSalary = self.getAmountFromSalaryStructure(abbr="BASE_SALARY")
        lunch = self.getAmountFromSalaryStructure(abbr="LUNCH")
        ngan = flt(baseSalary / 30, precision=2)

        presentOnWorkingDayCount = cint(srAttSummary["is_present_on_working_day"])
        lunchAmountUpdated = lunch * presentOnWorkingDayCount
        self.updateSalaryDetails("LUNCH", lunchAmountUpdated)

        absentCount = cint(srAttSummary["deduct_ngan_absent"])
        absentAmountUpdated = flt(ngan * absentCount, precision=2)
        self.updateSalaryDetails("ABSENT", absentAmountUpdated)

        nganLateCount = cint(srAttSummary["deduct_ngan_late"])
        lateNgan = flt(ngan * nganLateCount, precision=2)
        lateMin = 1 * cint(srAttSummary["late_min_for_deduct"])
        lateUpdateAmount = lateNgan + lateMin
        self.updateSalaryDetails("LATE", lateUpdateAmount)

        socialUpdateAmount = 0.05 * baseSalary if baseSalary < 15000 else 0.05 * 15000
        self.updateSalaryDetails("SOCIAL", socialUpdateAmount)

        salaryCalc = f"""-----------------------------------
ข้อมูล
- วันทำงาน = {srAttSummary["is_working_day"]} วัน
- ลาเต็มวัน = {srAttSummary["is_on_leave"]} วัน
- เข้างาน = {srAttSummary["is_present"]} วัน
- ขาดงาน = วันทำงาน - (เข้างาน + ลาเด็มวัน) = {absentCount} วัน
- มาทำงานในวันทำงาน = {presentOnWorkingDayCount} วัน
-----------------------------------
- เงินเดือน = {baseSalary} บาท
- งาน = {ngan} บาท 
- ค่าอาหารกลางวัน = {lunch} บาท (ต่อวัน)
-----------------------------------
การเพิ่มเงินเดือน
1) ค่าอาหารกลางวัน
- จำนวนวันที่มาทำงานในวันทำงาน x ค่าอาหารกลางวัน
- {presentOnWorkingDayCount} x {lunch} = {lunchAmountUpdated} บาท
-----------------------------------
การหักเงินเดือน
1) ประกันสังคม
- 5% ของฐานเงินเดือน (คิดเงินเดือนมากที่สุด 15000 บาท)
- 0.05 x {baseSalary if baseSalary < 15000 else 15000} = {socialUpdateAmount} บาท
2) เข้างานไม่ครบ
- จำนวนวันที่ขาดงาน x งาน
- {absentCount} x {ngan} = {absentAmountUpdated} บาท
3) เกินเวลา / มาสาย
- เข้างานเกินเวลา {lateMin} นาที หักเงิน {lateMin} บาท
- ปรับมาสายเป็นจำนวน {nganLateCount} งาน หักเงิน  {nganLateCount} x {ngan} = {lateNgan} บาท
- รวมการหักเงินเป็น {lateUpdateAmount} บาท
        """

        ####################################################################################
        # If you want to inject a new salary details
        ####################################################################################
        # sd = frappe.get_doc(
        #     {
        #         "doctype": "Salary Detail",
        #         "salary_component": "Deduction",
        #         "amount": 1000,
        #         "parent": self,
        #         "parenttype": "Salary Slip",
        #     }
        # )
        # self.append("deductions", sd)
        ####################################################################################

        self.calculate_net_pay()
        self.custom_salary_calc_details = salaryCalc
        pass
