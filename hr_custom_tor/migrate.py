import frappe


def after_migrate():
    # run code after site migration
    print("Running code after migration....")
    ps = frappe.get_doc("Payroll Settings")
    ps.payroll_based_on = "Attendance"
    ps.consider_unmarked_attendance_as = "Absent"
    ps.save()
    pass
