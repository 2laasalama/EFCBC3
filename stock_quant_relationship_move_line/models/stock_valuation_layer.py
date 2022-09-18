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


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    analytic_account_id = fields.Many2one("account.analytic.account",
                                          string="Analytic Account", compute='_compute_analytic_account_id',
                                          store=True
                                          )
    partner_id = fields.Many2one("res.partner",
                                 string="الشخص/الشركة", compute='_compute_analytic_account_id',
                                 store=True
                                 )

    @api.depends('stock_move_id')
    def _compute_analytic_account_id(self):
        for rec in self:
            rec.analytic_account_id = rec.partner_id = False
            if rec.stock_move_id:
                rec.analytic_account_id = rec.stock_move_id.analytic_account_id
                rec.partner_id = rec.stock_move_id.partner_id
