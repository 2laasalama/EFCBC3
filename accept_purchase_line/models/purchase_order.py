# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rejected_line_ids = fields.One2many('purchase.order.line', 'rejected_order_id', 'Rejected Lines')

    def button_confirm(self):
        for line in self.order_line.filtered(lambda l: not l.accept):
            line.rejected_order_id = line.order_id.id
            line.order_id = False


        if not self.order_line:
            raise ValidationError("You Can't Confirm this RFQ, Three is no any accepted line.")
        return super(PurchaseOrder, self).button_confirm()

    def button_draft(self):
        for rec in self:
            order_line = self.env['purchase.order.line'].search([('active', '=', False), ('order_id', '=', rec.id)])
            for line in order_line:
                line.active = True
        super(PurchaseOrder, self).button_draft()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    accept = fields.Boolean(default=True,string='موافق')
    active = fields.Boolean(default=True)
    rejected_order_id = fields.Many2one('purchase.order')
    order_id = fields.Many2one(required=False)
