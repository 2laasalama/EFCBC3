{
    'name': "Company Logo in Backend Navbar",
    'description': """
                    Adding the company logo to the Backend Navbar.
                   """,
    'license': "AGPL-3",
    'depends': [
        'base',
        'web',
    ],

    'data': [
        # 'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'web_company_logo/static/src/js/company_menu.js',
            'web_company_logo/static/src/scss/company_menu.scss',
        ],
        'web.assets_qweb': [
            'web_company_logo/static/src/xml/company_menu.xml',
        ],
    },
    'installable': True,
    'application': False,
}
