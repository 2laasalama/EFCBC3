# -*- coding: utf-8 -*-
{
    'name': "Unpacking RFQ",

    'summary': """Unpacking RFQ Report""",

    'author': "Mahmoud AbdElaziz",
    'license': 'OPL-1',
    'category': 'Purchase',
    'version': '0.2',
    'depends': ['purchase_requisition', 'efcbc_cutome_purchase','accept_purchase_line','report_xlsx'],

    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/unpacking_report.xml',
        'views/purchase_requisition.xml',
        'views/unpacking_rfq.xml',
    ],

}
