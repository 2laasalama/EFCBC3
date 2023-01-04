# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    parent_id = fields.Many2one('purchase.order')
    version_count = fields.Integer(compute='_compute_version_count')
    version = fields.Integer(defualt=1)

    def _compute_version_count(self):
        for rec in self:
            rec.version_count = self.search_count([('parent_id', '=', rec.id)])

    def create_version(self):
        self.ensure_one()
        order = self.copy()
        order.update({'parent_id': self.id, 'version': self.version_count + 1})
        return {
            'name': _("Requests for Quotation %s", order.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': order.id,
            'view_id': self.env.ref('purchase.purchase_order_form').id,
        }

    def open_version_list(self):
        self.ensure_one()
        orders = self.search([('parent_id', '=', self.id)])
        if orders:
            return {
                'name': _("Requests for Quotation"),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                "context": {"create": False},
                'res_model': 'purchase.order',
                'domain': [('id', 'in', orders.ids)]
            }
