# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_attachment_types(self):
        res = super(HrPayslip, self)._get_attachment_types()
        res.update({
            'rewards': self.env.ref('hr_salary_attachment.input_rewards'),
            'vacation_allowance': self.env.ref('hr_salary_attachment.input_vacation_allowance'),
            'night_allowance': self.env.ref('hr_salary_attachment.input_night_allowance'),
            'transportation_allowance': self.env.ref('hr_salary_attachment.input_transportation_allowance'),
            'quarter_incentive': self.env.ref('hr_salary_attachment.input_quarter_incentive'),
        })
        return res

    def get_input_lines(self, date_from, date_to):
        res = super(HrPayslip, self).get_input_lines(date_from, date_to)

        # Transportation
        transportation_line = self.env['hr.transportation.allowance.line'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'done'),
             ('date_from', '>=', date_from),
             ('date_from', '<=', date_to)])

        if transportation_line:
            vals = {
                'input_type_id': self.env.ref('hr_salary_attachment.input_transportation_allowance').id,
                'name': 'Transportation Allowance',
                'code': 'TRANS_ALLOW',
                'amount': transportation_line.net,
            }
            res.append((0, 0, vals))

        # Quarter Incentive
        quarter_incentive = self.env['hr.quarter.incentive.line'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'done'),
             ('date_from', '>=', date_from),
             ('date_from', '<=', date_to)])
        if quarter_incentive:
            vals = {
                'input_type_id': self.env.ref('hr_salary_attachment.input_quarter_incentive').id,
                'name': 'Quarter Incentive',
                'code': 'QUARTER_INCENTIVE',
                'amount': quarter_incentive.net,
            }
            res.append((0, 0, vals))

        return res
