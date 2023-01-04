{
    'name': 'EFCBC Backend Theme',
    'version': '15.0.1.0.1',
    'license': 'AGPL-3',
    'depends': ['web_enterprise'],
    'category': 'Branding',
    'description': """EFCBC Backend Enterprise Theme""",
    'data': {
        'templates/middle_login_template.xml',
    },
    'assets': {
        'web._assets_primary_variables': [
            '/efcbc_backend_theme/static/src/scss/primary_variables_custom.scss',
        ],
        'web._assets_common_styles': [
            ('replace', 'web_enterprise/static/src/legacy/scss/ui.scss',
             'efcbc_backend_theme/static/src/scss/ui.scss'),

        ],
        'web.assets_backend': [
            'efcbc_backend_theme/static/src/scss/webclient.scss'

        ], 'web.assets_frontend': [
            'efcbc_backend_theme/static/src/css/web_login_style.css'

        ],
    },
}

