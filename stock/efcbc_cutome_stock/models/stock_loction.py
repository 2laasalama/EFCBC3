# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
from datetime import datetime, timedelta
from itertools import product as cartesian_product
from collections import defaultdict

from odoo import models, api, fields
from odoo.tools import populate, groupby


class Location(models.Model):
    _inherit = 'stock.location'

    fixed_assets = fields.Boolean('أصول ثابتة')
    scrap_committee_approval = fields.Boolean('يتطلب موافقة لجنه كنهه')
    scrap_committee_member_ids = fields.Many2many('hr.employee', string='أعضاء اللجنة')
    finance_committee_approval = fields.Boolean('يتطلب  موافقة اللجنه المالية')
    finance_committee_member_ids = fields.Many2many('hr.employee', 'employee_finance_committee_rel', 'emp_id',
                                                    'location_id', string='أعضاء اللجنة')
