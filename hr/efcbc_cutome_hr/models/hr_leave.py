# -*- coding: utf-8 -*-
import calendar

from odoo import api, fields, models
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    exclude_penalty = fields.Boolean(related='holiday_status_id.exclude_penalty', store=True)
    exclude_weekends = fields.Boolean(related='holiday_status_id.exclude_weekends', store=True)
    exclude_holidays = fields.Boolean(related='holiday_status_id.exclude_holidays', store=True)
    payroll_summary = fields.Boolean(related='holiday_status_id.payroll_summary', store=True)
    leave_category = fields.Selection(
        [('annual', 'Annual Leaves'), ('other', 'Other Leaves'), ('permission', 'Permission'), ('mission', 'Mission')],
        store=True, related='holiday_status_id.leave_category'
    )

    @api.onchange('holiday_status_id', 'exclude_weekends', 'exclude_holidays')
    def recompute_no_days(self):
        self._compute_number_of_days()

    def _get_number_of_days(self, date_from, date_to, employee_id):
        context_data = {'exclude_weekends': False, 'exclude_holidays': False}

        if self.holiday_status_id.exclude_weekends or not self.holiday_status_id:
            context_data['exclude_weekends'] = True

        if self.holiday_status_id.exclude_holidays or not self.holiday_status_id:
            context_data['exclude_holidays'] = True

        instance = self.with_context(context_data)
        return super(HrLeave, instance)._get_number_of_days(date_from, date_to, employee_id)
