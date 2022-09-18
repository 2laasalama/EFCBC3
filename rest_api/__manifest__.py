{
    'name': 'REST API For odoo',
    'version': '1.0.0',
    'category': 'API',
    'author': 'odooHQ',
    'website': 'https://www.odoohq.com',
    'summary': 'REST API For odoo',
    'description': """
REST API For odoo
====================
With use of this module user can enable REST API in any odoo applications/modules

For detailed example of REST API refer *readme.md*
""",
    'depends': [
        'web',
    ],
    'data': [
        'data/ir_configparameter_data.xml',
        'views/ir_model_view.xml',
        'views/res_user_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
