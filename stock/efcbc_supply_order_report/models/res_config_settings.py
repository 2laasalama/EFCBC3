# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    executive_secretariat_image = fields.Binary(related='company_id.executive_secretariat_image', readonly=False )
