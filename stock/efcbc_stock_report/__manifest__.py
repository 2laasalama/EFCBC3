# -*- coding: utf-8 -*-
{
    'name': "EFCBC Stock Report",
    'license': 'AGPL-3',
    'summary': """Custom Report for EFCBC""",
    'category': 'stock',
    'version': '0.1',
    'depends': ['stock_analytic', 'efcbc_report_layout', 'efcbc_cutome_stock'],
    'data': [
        'data/report_layout.xml',
        'report/receipt_order_report.xml',
        'report/return_order_report.xml',
        'report/delivery_order_report.xml',
        'report/maintenance_order_report.xml',
        'report/inventory_adjustments_report.xml',
        'report/general_order_report.xml',
        'views/stock_picking_views.xml',
        'views/stock_picking_type.xml',
    ]
}
