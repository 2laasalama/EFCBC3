# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR, AND

from odoo.addons.web.controllers.main import HomeStaticTemplateHelpers


class ApprovalCustomerPortal(CustomerPortal):

    def _prepare_approval_sharing_session_info(self):
        session_info = request.env['ir.http'].session_info()
        user_context = request.session.get_context() if request.session.uid else {}
        mods = conf.server_wide_modules or []
        qweb_checksum = HomeStaticTemplateHelpers.get_qweb_templates_checksum(debug=request.session.debug,
                                                                              bundle="approval_portal.assets_qweb")
        if request.env.lang:
            lang = request.env.lang
            session_info['user_context']['lang'] = lang
            user_context['lang'] = lang
        lang = user_context.get("lang")
        translation_hash = request.env['ir.translation'].get_web_translations_hash(mods, lang)
        cache_hashes = {
            "qweb": qweb_checksum,
            "translations": translation_hash,
        }

        company = request.env['res.users'].browse(request.session.uid).company_id

        session_info.update(
            cache_hashes=cache_hashes,
            action_name='approvals.approval_category_action_new_request',
            user_companies={
                'current_company': company.id,
                'allowed_companies': {
                    company.id: {
                        'id': company.id,
                        'name': company.name,
                    },
                },
            },
        )
        return session_info

    @http.route("/my/approvals", type="http", auth="user", methods=['GET'])
    def render_approval_backend_view(self):
        return request.render(
            'approval_portal.approval_sharing_embed',
            {'session_info': self._prepare_approval_sharing_session_info()},
        )

