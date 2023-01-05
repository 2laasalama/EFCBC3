{
    "name": "Account Audit",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Account Audit",
    "author": "Mahmoud Abdelaziz",
    'license': 'LGPL-3',
    "depends": ["efcbc_custom_account",'hr_expense'],
    "data": [
        "security/ir.model.access.csv",
        "views/payment_order.xml",
        "views/hr_expense_sheet.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
