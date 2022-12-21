# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Leave maximum amount of accruals to transfer",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "author": "Mahmoud Abdelaziz",
    "depends": ['hr_holidays'],
    "data": [
        "views/hr_leave_accrual_plan_level.xml",
    ],
    "application": True,
}
