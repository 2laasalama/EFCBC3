# -*- coding: utf-8 -*-
{
    'name': "EFCBC Report Layout",

    'summary': """Custom Report Layout for EFCBC""",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'data/report_layout.xml',
    ],
    'assets': {

        'web.report_assets_common': [
            'efcbc_report_layout/static/src/scss/layout.scss',
            'efcbc_report_layout/static/src/css/layout.css',
        ],
    },
}
