# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_attachment_types(self):
        res = super(HrPayslip, self)._get_attachment_types()
        res.update({
            'travelling_allowance': self.env.ref('hr_travelling_allowance.input_travelling_allowance'),
        })
        return res

    def get_input_lines(self, date_from, date_to):
        res = super(HrPayslip, self).get_input_lines(date_from, date_to)

        travelling_line = self.env['hr.travelling.allowance'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'done'),
             ('date', '>=', date_from),
             ('date', '<=', date_to)])

        if travelling_line:
            vals = {
                'input_type_id': self.env.ref('hr_travelling_allowance.input_travelling_allowance').id,
                'name': 'Travelling Allowance',
                'code': 'TRAVEL_ALLOW',
                'amount': travelling_line.total_amount,
            }
            res.append((0, 0, vals))

        return res
