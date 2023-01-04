# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_attachment_types(self):
        res = super(HrPayslip, self)._get_attachment_types()
        res.update({
            'medical_claims': self.env.ref('hr_medical_claims.input_medical_claims'),
        })
        return res

    def get_input_lines(self, date_from, date_to):
        res = super(HrPayslip, self).get_input_lines(date_from, date_to)

        medical_line = self.env['hr.medical.claims.line'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'done'),
             ('provider_category', '=', 'other'),
             ('date', '>=', date_from),
             ('date', '<=', date_to)])

        if medical_line:
            vals = {
                'input_type_id': self.env.ref('hr_medical_claims.input_medical_claims').id,
                'name': 'Medical Claims',
                'code': 'MEDICAL_CLAIMS',
                'amount': medical_line.actual_amount,
            }
            res.append((0, 0, vals))

        return res
