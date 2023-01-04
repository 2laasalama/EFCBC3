# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
from datetime import datetime, timedelta
from itertools import product as cartesian_product
from collections import defaultdict

from odoo import models, api, fields
from odoo.tools import populate, groupby


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_ref = fields.Char(string='كود الصنف', related='product_id.default_code')
    accept = fields.Boolean(string='موافق')
    carry_on = fields.Boolean(string='يحمل على المتسبب')
