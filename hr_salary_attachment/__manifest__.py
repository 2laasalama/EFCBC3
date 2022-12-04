# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Salary Attachment Customization",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "author": "Mahmoud Abdelaziz",
    "depends": ['efcbc_cutome_hr', 'efcbc_report_layout'],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_salary_attachment.xml",
        "wizard/salary_attachment_report_wizard.xml",
        # "report/report.xml",
        "report/salary_attachment_report.xml",
    ],
    "application": True,
}
