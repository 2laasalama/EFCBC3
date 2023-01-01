# -*- coding: utf-8 -*-
{
    'name': "EFCBC Cutome Purchase",
    'license': 'AGPL-3',
    'summary': """EFCBC Cutome Purchase""",
    'author': "Mahmoud AbdElaziz",
    'license': 'OPL-1',
    'category': 'Purchase',
    'version': '0.2',
    'depends': ['purchase', 'purchase_requisition','purchase_requisition_stock','hr'],
    'data': [
        'security/security_groups.xml',
        'data/sequence.xml',
        'views/purchase_view.xml',
        'views/product_template.xml',
        'views/purchase_requisition.xml',
        'views/purchase_requisition_type.xml',
        'views/hr_employee.xml',
    ],

}
