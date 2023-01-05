# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_order_sequence = fields.Many2one('ir.sequence', related='company_id.payment_order_sequence', readonly=False)
    payment_permission_sequence = fields.Many2one('ir.sequence', related='company_id.payment_permission_sequence',
                                                  readonly=False)
