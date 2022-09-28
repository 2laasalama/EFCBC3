# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_order_id = fields.Many2one('purchase.order', compute='_compute_purchase_order')
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.depends('move_ids_without_package')
    def _compute_purchase_order(self):
        for rec in self:
            purchase_order_lines = rec.move_ids_without_package.mapped('purchase_line_id')
            if purchase_order_lines:
                rec.purchase_order_id = purchase_order_lines[0].order_id
            else:
                rec.purchase_order_id = False

    def action_set_quantities_to_reservation(self):
        super(StockPicking, self).action_set_quantities_to_reservation()
        for line in self.move_ids_without_package:
            line.check_accept_purchase_qty()

    def button_validate(self):
        for line in self.move_ids_without_package:
            line.check_accept_purchase_qty()
        if self.purchase_order_id and self.purchase_order_id.require_committee_approval:
            return super(StockPicking, self.with_context(skip_backorder=True)).button_validate()
        else:
            return super(StockPicking, self).button_validate()

    @api.model
    def create(self, vals):
        picking = super(StockPicking, self).create(vals)
        origin = picking.backorder_id
        if origin and origin.purchase_order_id and origin.purchase_order_id.require_committee_approval:
            picking.active = False
        return picking
