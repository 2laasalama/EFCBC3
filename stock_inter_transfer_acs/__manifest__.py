# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Inter Warehouse Transfer",
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Inter Warehouse Transfer',
    'description': """
    Transfer stock from one warehouse to another warehouse
    """,
    'author': 'Aurayan Consulting Services',
    'website': '',
    'depends': ['stock'],
    'data': [
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "views/stock_transfer_view.xml",
        "views/stock_picking_view.xml",
        "views/res_config_settings_view.xml"
    ],
    'images': ['static/description/main_screen.png'],
    'price': 70.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}