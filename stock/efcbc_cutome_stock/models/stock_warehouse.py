# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
from datetime import datetime, timedelta
from itertools import product as cartesian_product
from collections import defaultdict

from odoo import models, api, fields
from odoo.tools import populate, groupby


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    type = fields.Selection(
        string='النوع',
        selection=[('stock', 'مخازن'),
                   ('assets', 'اصول'),
                   ('custody', 'عهد'),
                   ('maintenance', 'صيانة'),
                   ('scrap', 'كهنه'), ],
        default='stock')
