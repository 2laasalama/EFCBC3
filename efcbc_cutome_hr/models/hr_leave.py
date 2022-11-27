# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    exclude_penalty = fields.Boolean(related='holiday_status_id.exclude_penalty')
    exclude_weekends = fields.Boolean(related='holiday_status_id.exclude_weekends')
    exclude_holidays = fields.Boolean(related='holiday_status_id.exclude_holidays')

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
