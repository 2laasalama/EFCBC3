# -*- coding: utf-8 -*-
{
    'name': 'Approval Portal',
    'version': '1.0',
    'sequence': '10',
    'category': 'Portal',
    'summary': 'Approval Portal',
    'depends': ['portal', 'approvals', 'web', 'mail', 'bus','website'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/approval_portal_templates.xml',
        'views/approval_sharing_templates.xml',
    ],
    'assets': {
        'approval_portal.assets_qweb': [
            ('include', 'web.assets_qweb'),
            'approval_portal/static/src/project_sharing/**/*.xml',
        ],
        'approval_portal.webclient': [
            ('include', 'web.assets_backend'),

            # Remove Longpolling bus and packages needed this bus
            ('remove', 'bus/static/src/js/services/assets_watchdog_service.js'),
            ('remove', 'mail/static/src/services/messaging/messaging.js'),

            ('remove', 'mail/static/src/components/dialog_manager/dialog_manager.js'),
            ('remove', 'mail/static/src/services/dialog_service/dialog_service.js'),
            ('remove', 'mail/static/src/components/chat_window_manager/chat_window_manager.js'),
            ('remove', 'mail/static/src/services/chat_window_service/chat_window_service.js'),

            'web/static/src/legacy/js/public/public_widget.js',
            'portal/static/src/js/portal_chatter.js',
            'portal/static/src/js/portal_composer.js',
            'approval_portal/static/src/project_sharing/search/favorite_menu/custom_favorite_item.xml',
            'approval_portal/static/src/project_sharing/**/*.js',
            'approval_portal/static/src/scss/project_sharing/*',
            'web/static/src/start.js',
            'web/static/src/legacy/legacy_setup.js',
        ],
    },
}
