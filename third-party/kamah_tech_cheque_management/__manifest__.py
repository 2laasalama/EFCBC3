# -*- coding: utf-8 -*-
{
    'name': "Check Management v15",

    'summary': """ Check Management v15""",

    'description': """
        This Module is used for check \n
        It includes creation of check receipt ,check cycle ,Holding ....... \n

    """,

    'author': "Ahmed Farid",
    'website': "http://www.kamah-tech.com/",

    # Categories can be used to filter modules in modules listing
    # Check 
    # for the full list
    'category': 'Accounting',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_journal_view.xml',
        'views/checks_fields_view.xml',
        'views/check_payment.xml',
        'views/check_menus.xml',
        'wizard/check_cycle_wizard_view.xml',
        'views/payment_report.xml',
        'views/report_check_cash_payment_receipt_templates.xml',


    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'GPL-3',
    'price': 800.0,
    'currency': 'EUR',
    'application': True,

}
