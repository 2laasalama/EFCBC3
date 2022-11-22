# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    date = fields.Date(compute='compute_date', store=False)

    @api.onchange('check_in')
    def compute_date(self):
        for rec in self:
            rec.date = rec.check_in.date()
