# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_ratio = fields.Float(config_parameter='efcbc_cutome_hr.tax_ratio', default=10)
