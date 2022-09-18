# -*- coding: utf-8 -*-
{
    'name': 'Multi Purchase Order approval',
    'version': '12.0.1.0.0',
    'summary': """Manages Multi Purchase Order approval""",
    'author': 'Mahmoud Abdelaziz',
    'depends': ['base','efcbc_cutome_purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/po_approval_level.xml',
        'views/res_config_settings_views.xml',
        # 'views/purchase_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

