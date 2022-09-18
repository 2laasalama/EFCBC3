{
    'name': 'BBM Endpoints',
    'version': '1.0.0',
    'category': 'API',
    'depends': ['rest_api', 'base', 'account'],
    'data': [
        'views/res_partner_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
