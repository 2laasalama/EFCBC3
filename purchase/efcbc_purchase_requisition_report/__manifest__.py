# -*- coding: utf-8 -*-
{
    'name': "EFCBC Purchase Requisition Report",

    'summary': """Custom Report for EFCBC""",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['efcbc_cutome_purchase', 'analytic', 'efcbc_report_layout', 'purchase_committee_approval'],
    'data': [
        'data/report_layout.xml',
        'report/purchase_requisition_report.xml',
        'views/purchase_requisition.xml',
    ]
}
