# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_description = fields.Char('وصف الصنف')

    @api.model
    def create(self, vals):
        move = super(StockMove, self).create(vals)
        if 'purchase_line_id' in vals:
            analytic_account_id = move.purchase_line_id.order_id.analytic_account_id
            move.write({'product_description': move.purchase_line_id.name,
                        'analytic_account_id': analytic_account_id})
        return move

    def _compute_is_quantity_done_editable(self):
        for move in self:
            move.is_quantity_done_editable = True
            if move.picking_id.is_locked or move.state in ('done', 'cancel'):
                move.is_quantity_done_editable = False
