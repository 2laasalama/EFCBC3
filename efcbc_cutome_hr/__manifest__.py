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
                'hr_holidays', ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/hr_leave_type.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'efcbc_cutome_hr/static/src/xml/**/*',
        ],
    },

}
