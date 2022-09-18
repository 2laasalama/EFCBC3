# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
from datetime import datetime, timedelta
from itertools import product as cartesian_product
from collections import defaultdict

from odoo import models, api, fields
from odoo.tools import populate, groupby


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    fixed_assets = fields.Boolean(compute='_compute_fixed_assets', store=True)
    return_operation = fields.Boolean(string='عملية إرجاع')
    is_maintenance = fields.Boolean(string='أمر صيانة')

    @api.depends('default_location_src_id', 'default_location_dest_id', 'default_location_src_id.fixed_assets',
                 'default_location_dest_id.fixed_assets')
    def _compute_fixed_assets(self):
        for rec in self:
            rec.fixed_assets = False
            if rec.default_location_src_id and rec.default_location_src_id.fixed_assets:
                rec.fixed_assets = True
            if rec.default_location_dest_id and rec.default_location_dest_id.fixed_assets:
                rec.fixed_assets = True
