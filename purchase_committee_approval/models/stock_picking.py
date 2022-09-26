# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.picking'

    is_purchase_order = fields.Boolean(compute='_compute_purchase_order')

    @api.depends('move_ids_without_package')
    def _compute_purchase_order(self):
        for rec in self:
            rec.is_purchase_order = True if rec.move_ids_without_package.mapped('purchase_line_id') else False

    def action_set_quantities_to_reservation(self):
        super(StockMove, self).action_set_quantities_to_reservation()
        for line in self.move_ids_without_package:
            line.check_accept_purchase_qty()

    def button_validate(self):
        for line in self.move_ids_without_package:
            line.check_accept_purchase_qty()
        return super(StockMove, self).button_validate()
