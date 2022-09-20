# -*- coding: utf-8 -*-
{
    'name': "Purchase Committee approval",

    'summary': """Purchase Committee approval""",

    'author': "Mahmoud AbdElaziz",
    'license': 'OPL-1',
    'category': 'Purchase',
    'version': '0.2',
    'depends': ['purchase_stock', 'hr', 'rfq_workflow', 'efcbc_report_layout'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/purchase_order.xml',
        'views/purchase_requisition_views.xml',
        'views/stock_view.xml',
        'wizard/purchase_committee_approval.xml',
        'wizard/rfq_unpacking_approval.xml',
        'report/check_receipt_report.xml',
    ],

}
