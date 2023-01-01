# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Employee Rewards",
    "version": "15.0.0.0.0",
    "category": "Payroll",
    "sequence": 11,
    "author": "Mahmoud Abdelaziz",
    "depends": ['efcbc_cutome_hr', 'hr_work_entry_contract_enterprise'],
    "data": [
        # "data/hr_payroll_data.xml",
        "security/ir.model.access.csv",
        "wizard/hr_employee_rewards_employees.xml",
        "views/hr_employee_rewards.xml",
    ],
    "application": True,
}
