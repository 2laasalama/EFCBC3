# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

try:
    from oauthlib import common as oauthlib_common
except ImportError:
    _logger.warning(
        'OAuth library not found. If you plan to use it, '
        'please install the oauth library from '
        'https://pypi.python.org/pypi/oauthlib')


class ResUsers(models.Model):
    _inherit = 'res.users'

    token = fields.Char('Access Token')
    expire_date = fields.Datetime('Expire In')

    def generate_token(self):
        if not self.expire_date or datetime.now() >= self.expire_date:
            expires = datetime.now() + timedelta(
                seconds=int(self.env.ref('rest_api.oauth2_access_token_expires_in').sudo().value))
            token = oauthlib_common.generate_token()
            self.sudo().update({
                'expire_date': expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'token': token,
            })
