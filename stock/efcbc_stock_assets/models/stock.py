# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
from datetime import datetime, timedelta
from itertools import product as cartesian_product
from collections import defaultdict

from odoo import models, api, fields,_
from odoo.tools import populate, groupby


class Location(models.Model):
    _inherit = 'stock.location'

    fixed_assets = fields.Boolean('أصول ثابتة')


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    fixed_assets = fields.Boolean(compute='_compute_fixed_assets', store=True)

    @api.depends('default_location_src_id', 'default_location_dest_id','default_location_src_id.fixed_assets', 'default_location_dest_id.fixed_assets')
    def _compute_fixed_assets(self):
        for rec in self:
            rec.fixed_assets = False
            if rec.default_location_src_id and rec.default_location_src_id.fixed_assets:
                rec.fixed_assets = True
            if rec.default_location_dest_id and rec.default_location_dest_id.fixed_assets:
                rec.fixed_assets = True
