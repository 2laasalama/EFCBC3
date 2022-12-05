# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Salary Attachment Customization",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "author": "Mahmoud Abdelaziz",
    "depends": ['hr_payroll_summary', 'rm_eg_hr_payroll'],
    "data": [
        "security/ir.model.access.csv",
        "wizard/salary_attachment_report_wizard.xml",
        "views/hr_salary_attachment.xml",
        "views/hr_transportation_allowance.xml",
        "views/hr_quarter_incentive.xml",
        "report/salary_attachment_report.xml",
        "report/transportation_allowance_report.xml",
        "report/quarter_incentive_report.xml",
    ],
    "application": True,
}
