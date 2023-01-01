# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
from datetime import datetime, timedelta
from itertools import product as cartesian_product
from collections import defaultdict

from odoo import models, api, fields
from odoo.tools import populate, groupby
from odoo.tools import float_compare, float_round


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    move_line_ids = fields.Many2many('stock.move.line',string='Move Lines')
    analytic_account_ids = fields.Many2many("account.analytic.account",
                                            string="الجهة الطالبة", compute='_compute_analytic_account_id',
                                            store=True
                                            )
    partner_ids = fields.Many2many("res.partner",
                                            string="الشخص/الشركة", compute='_compute_analytic_account_id',
                                            store=True
                                            )
    product_categ_id = fields.Many2one(related='product_tmpl_id.categ_id',string='Product Category',store=True)


    @api.depends('move_line_ids')
    def _compute_analytic_account_id(self):
        for rec in self:
            rec.analytic_account_ids = False
            rec.partner_ids = False
            analytic_account_ids = []
            partner_ids = []
            for line in rec.move_line_ids:
                if rec.location_id == line.location_dest_id and line.analytic_account_id:
                    analytic_account_ids.append(line.analytic_account_id.id)
                if line.partner_id:
                    partner_ids.append(line.partner_id.id)
            rec.analytic_account_ids = [(6, 0, analytic_account_ids)]
            rec.partner_ids = [(6, 0, partner_ids)]

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None,
                                   in_date=None, ml=None):

        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                              strict=True)
        if lot_id and quantity > 0:
            quants = quants.filtered(lambda q: q.lot_id)

        if quants and ml:
            quants.move_line_ids |= ml

        return super(StockQuant, self)._update_available_quantity(product_id, location_id, quantity, lot_id, package_id,
                                                                  owner_id,
                                                                  in_date)

        if location_id.should_bypass_reservation():
            incoming_dates = []
        else:
            incoming_dates = [quant.in_date for quant in quants if quant.in_date and
                              float_compare(quant.quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = min(incoming_dates)
        else:
            in_date = fields.Datetime.now()

        quant = None
        if quants:
            # see _acquire_one_job for explanations
            self._cr.execute(
                "SELECT id FROM stock_quant WHERE id IN %s ORDER BY lot_id LIMIT 1 FOR NO KEY UPDATE SKIP LOCKED",
                [tuple(quants.ids)])
            stock_quant_result = self._cr.fetchone()
            if stock_quant_result:
                quant = self.browse(stock_quant_result[0])

        if quant:
            quant.write({
                'quantity': quant.quantity + quantity,
                'in_date': in_date,
            })
        else:
            self.create({
                'product_id': product_id.id,
                'location_id': location_id.id,
                'quantity': quantity,
                'lot_id': lot_id and lot_id.id,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
                'move_line_ids': ml and ml.id,
            })
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id,
                                            owner_id=owner_id, strict=False, allow_negative=True), in_date
