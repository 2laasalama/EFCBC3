# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Medical Claims",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "author": "Mahmoud Abdelaziz",
    "depends": ['efcbc_cutome_hr'],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/hr_medical_claims.xml",
        "report/medical_claims_report.xml",
    ],
    "application": True,
}
