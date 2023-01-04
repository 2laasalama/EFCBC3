# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_attachment_types(self):
        res = super(HrPayslip, self)._get_attachment_types()
        res.update({
            'committee_allowance': self.env.ref('hr_committee.input_committee_allowance'),
        })
        return res

    def get_input_lines(self, date_from, date_to):
        res = super(HrPayslip, self).get_input_lines(date_from, date_to)

        committee_line = self.env['hr.committee.line'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'done'),
             ('date_from', '>=', date_from),
             ('date_from', '<=', date_to)])

        if committee_line:
            vals = {
                'input_type_id': self.env.ref('hr_committee.input_committee_allowance').id,
                'name': 'Committee Allowance',
                'code': 'COMMITTEE_ALLOW',
                'amount': committee_line.net_pay,
            }
            res.append((0, 0, vals))

        return res
