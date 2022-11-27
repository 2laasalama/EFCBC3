# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Payroll Summary",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "summary": "Manage your employee payroll records",
    "author": "Mahmoud Abdelaziz",
    "depends": ['date_range', 'efcbc_cutome_hr', 'rm_hr_attendance_sheet'],
    "data": [
        "security/ir.model.access.csv",
        "wizard/hr_payslips_summary_employees.xml",
        "views/hr_payslip_summary_views.xml",
        "views/hr_lateness_penalty_report.xml",
        "views/res_config_settings_views.xml",
        "report/payslip_summary_report.xml",
    ],
    "application": True,
}
