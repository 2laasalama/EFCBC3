# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    accept_purchase_qty = fields.Float(string='الكمية المقبولة من لجنة الاستلام', related='purchase_line_id.accept_qty',
                                       readonly=True)

    @api.model
    def create(self, vals):
        move = super(StockMove, self).create(vals)
        if 'purchase_line_id' in vals:
            move.write({'quantity_done': move.purchase_line_id.accept_qty})
        return move

    def check_accept_purchase_qty(self):
        for rec in self:
            if rec.purchase_line_id and rec.purchase_line_id.order_id.require_committee_approval:
                if rec.quantity_done != rec.accept_purchase_qty:
                    raise ValidationError("{} : Sorry you must accept only {}.".format(rec.product_id.name,
                                                                                       rec.accept_purchase_qty))
