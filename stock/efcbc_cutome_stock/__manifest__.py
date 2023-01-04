# -*- coding: utf-8 -*-
{
    'name': "EFCBC Cutome Stock",
    'license': 'AGPL-3',
    'summary': """EFCBC Cutome Stock""",
    'author': "Mahmoud AbdElaziz",
    'license': 'OPL-1',
    'category': 'Purchase',
    'version': '0.2',
    'depends': ['stock','stock_enterprise'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_view.xml',
        'views/product_template.xml',
        'views/picking_type_view.xml',
        'views/stock_quant.xml',
        'views/stock_location.xml',
        'views/stock_warehouse.xml',
        'wizard/scrap_committee_approval.xml',
    ],

}
