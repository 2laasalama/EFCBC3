# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Purchase Multi Warehouse Odoo App",
    'version': '15.0.0.1',
    'category': 'Purchase',
    'summary': 'Purchase order Multi Warehouse for purchase order line multi warehouse purchase order multiple warehouse purchase order line by warehouse selection purchase line warehouse PO line warehouse selection on purchase line multi warehouse option on purchase',
    "description": """ This odoo app helps user to select multiple warehouse for purchase order and create incoming shipment order based on warehouse selected on purchase order line, User have to configure warehouse on product and on selecting product on purchase order line warehouse will selected, user can also change warehouse. """,
    'author': 'Browseinfo',
    'website': "https://www.browseinfo.in",
    "price": 25,
    "currency": 'EUR',
    'depends': ['base', 'efcbc_cutome_stock', 'purchase_stock', 'purchase_requisition'],
    'data': [
        # 'views/purchase_config_settings_views.xml',
        'views/product_template_inherit.xml',
        'views/product_product_inherit.xml',
        'views/purchase_order_views.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/hzPjov3kjzk',
    "images": ['static/description/Banner.png'],
    'license': 'OPL-1',
}
