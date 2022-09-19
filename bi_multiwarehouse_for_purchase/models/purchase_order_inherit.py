# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, SUPERUSER_ID, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    is_multiwarehouse = fields.Boolean(string='Multi Wahouse', states=Purchase.READONLY_STATES, )

    def _onchange_requisition_id(self):
        super(PurchaseOrderInherit, self)._onchange_requisition_id()
        for line in self.order_line:
            line.set_required_warehouse()

    def _create_picking(self):
        if not self.is_multiwarehouse:
            return super(PurchaseOrderInherit, self)._create_picking()
        ok = []
        StockPicking = self.env['stock.picking']
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                order = order.with_company(order.company_id)
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                wh_ids = []
                if not pickings:
                    [wh_ids.append(x.warehouses_id) for x in order.order_line if x.warehouses_id not in wh_ids]
                    for wh_id in wh_ids:
                        po_lines = self.env['purchase.order.line'].search(
                            [('warehouses_id', '=', wh_id.id), ('order_id', '=', self.id)])
                        res = order.prepare_picking(po_lines[0])
                        picking = StockPicking.create(res)
                        ok += picking
                else:
                    ok = pickings[0]
                lines = []
                for wh_id in wh_ids:
                    po_lines = self.env['purchase.order.line'].search(
                        [('warehouses_id', '=', wh_id.id), ('order_id', '=', self.id)])
                    for i in ok:
                        if i.location_dest_id.warehouse_id.id == wh_id.id:
                            moves = po_lines.create_stock_moves(i)
                            moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                            seq = 0
                            for move in sorted(moves, key=lambda move: move.date):
                                seq += 5
                                move.sequence = seq
                            moves._action_assign()
                            i.message_post_with_view('mail.message_origin_link',
                                                     values={'self': i, 'origin': order},
                                                     subtype_id=self.env.ref('mail.mt_note').id)
        return True

    def prepare_picking(self, i):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))

        # search picking type based on selected warehouse in lines.
        picking_type_id = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', i.warehouses_id.id), ('return_operation', '=', False), ('code', '=', 'incoming')],
            limit=1)

        if not picking_type_id:
            raise UserError(_("You must set define Receipts operation for this  warehouses %s", i.warehouses_id.name))

        return {
            'picking_type_id': picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': i.warehouses_id.lot_stock_id.id,
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }
