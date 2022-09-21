# -*- coding: utf-8 -*-
{
    'name': "EFCBC Supply Order Report",
    'license': 'AGPL-3',
    'summary': """Custom Report for EFCBC""",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['purchase_requisition', 'efcbc_cutome_purchase', 'stock', 'hr', 'efcbc_report_layout'],
    'data': [
        'security/ir.model.access.csv',
        'report/supply_order_report.xml',
        'report/work_assignment_order_report.xml',
        'report/supply_work_order_report.xml',
        'views/purchase_order.xml',
        'views/purchase_requisition_views.xml',
        'views/res_config.xml',
    ]
}
