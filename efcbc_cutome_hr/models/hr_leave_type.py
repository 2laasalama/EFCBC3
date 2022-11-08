# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HRLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    exclude_penalty = fields.Boolean("Excluded in Time-off Penalty")
    exclude_weekends = fields.Boolean()
    exclude_holidays = fields.Boolean()
