# -*- coding: utf-8 -*-

from odoo import models, api, fields


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    report_id = fields.Many2one('ir.actions.report', string='Report', domain=[('is_stock_report', '=', True)])
    report_name = fields.Char()
    report_signature = fields.Char()
