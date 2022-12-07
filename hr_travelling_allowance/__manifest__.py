# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Travelling Allowance",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "author": "Mahmoud Abdelaziz",
    "depends": ['efcbc_cutome_hr'],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/hr_travelling_allowance.xml",
        "views/hr_travelling_route.xml",
        # "report/medical_claims_report.xml",
    ],
    "application": True,
}
