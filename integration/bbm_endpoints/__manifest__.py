{
    'name': 'BBM Endpoints',
    'version': '1.0.0',
    'category': 'API',
    'depends': ['rest_api', 'base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_configparameter_data.xml',
        'views/res_partner_views.xml',
        'views/account_payment_views.xml',
        'views/bpm_request.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
