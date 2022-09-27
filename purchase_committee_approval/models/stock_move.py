# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    accept_purchase_qty = fields.Float(string='الكمية المقبولة من لجنة الاستلام', copy=False, readonly=True)

    @api.model
    def create(self, vals):
        move = super(StockMove, self).create(vals)
        cancel_backorder = self.env.context.get('cancel_backorder', False)
        if not cancel_backorder and 'purchase_line_id' in vals:
            move.write({
                'quantity_done': move.purchase_line_id.accept_qty,
                'accept_purchase_qty': move.purchase_line_id.accept_qty
            })
        return move

    def check_accept_purchase_qty(self):
        for rec in self:
            if rec.purchase_line_id and rec.purchase_line_id.order_id.require_committee_approval:
                if rec.quantity_done != rec.accept_purchase_qty:
                    raise ValidationError("{} : Sorry you must accept only {}.".format(rec.product_id.name,
                                                                                       rec.accept_purchase_qty))
