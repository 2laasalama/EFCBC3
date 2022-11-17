# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    duration = fields.Char(compute='_compute_duration')

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for rec in self:
            date_end = date.today() if not rec.date_end else rec.date_end
            duration = relativedelta(date_end, rec.date_start)
            rec.duration = "{} Years {} Months {} Days".format(duration.years, duration.months,
                                                               duration.days)
