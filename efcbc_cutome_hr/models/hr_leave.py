# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HRLeave(models.Model):
    _inherit = 'hr.leave'

    exclude_penalty = fields.Boolean(related='holiday_status_id.exclude_penalty')
    exclude_weekends = fields.Boolean(related='holiday_status_id.exclude_weekends')
    exclude_holidays = fields.Boolean(related='holiday_status_id.exclude_holidays')
