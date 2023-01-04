# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    motivation_ratio = fields.Float(related='company_id.motivation_ratio', readonly=False)
    effort_ratio = fields.Float(related='company_id.effort_ratio', readonly=False)
