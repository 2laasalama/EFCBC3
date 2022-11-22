# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HRLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    exclude_penalty = fields.Boolean("Excluded in Time-off Penalty")
    exclude_weekends = fields.Boolean(default=True,
                                      help=(
                                          'If enabled, weekends are skipped in leave days'
                                          ' calculation.'
                                      ), )
    exclude_holidays = fields.Boolean("Exclude Public Holidays", default=True,
                                      help=(
                                          'If enabled,  Public Holidays are skipped in leave days'
                                          ' calculation.'
                                      ), )
    payroll_summary = fields.Boolean('Show in Payroll Summary', default=True)
