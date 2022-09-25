# -*- coding: utf-8 -*-
{
    'name': "EFCBC RFQ Report",
    'license': 'AGPL-3',
    'summary': """Custom Report for EFCBC""",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['efcbc_cutome_purchase', 'efcbc_report_layout'],
    'data': [
        'report/rfq_report.xml',
        'views/purchase_requisition_views.xml',
        'views/purchase_order.xml',
    ]
}
