# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Committees",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "author": "Mahmoud Abdelaziz",
    "depends": ['date_range', 'efcbc_cutome_hr', 'efcbc_report_layout'],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_committee.xml",
        "report/report.xml",
        "report/hr_committee_report.xml",
    ],
    "application": True,
}
