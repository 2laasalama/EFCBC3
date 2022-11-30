# -*- coding: utf-8 -*-
{
    'name': "EFCBC Cutome HR",
    'license': 'AGPL-3',
    'summary': """EFCBC Cutome HR""",
    'author': "Mahmoud AbdElaziz",
    'license': 'OPL-1',
    'category': 'HR',
    'version': '0.1',
    'depends': ['hr_skills', 'hr_payroll',
                'hr_holidays', 'date_range'],
    'data': [
        'data/excessive_leave_policy.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/hr_leave_type.xml',
        'views/excessive_leave_policy.xml',
        'views/excessive_leave.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'efcbc_cutome_hr/static/src/xml/**/*',
        ],
    },

}
