# -*- coding: utf-8 -*-
import babel
import time
from datetime import datetime

from odoo import models, Command, fields, api, tools, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_attachment_types(self):
        res = super(HrPayslip, self)._get_attachment_types()
        res.update({
            'motivation': self.env.ref('hr_payroll_summary.input_motivation'),
            'efforts': self.env.ref('hr_payroll_summary.input_efforts'),
        })
        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        self.input_line_ids = self.get_inputs(self.date_from, self.date_to)

    def get_inputs(self, date_from, date_to):
        res = []

        summary_line = self.env['hr.payslip.summary.line'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'done'),
             ('date_from', '>=', date_from),
             ('date_from', '<=', date_to)])
        if summary_line and self.contract_id:
            # Motivation
            amount = summary_line.motivation_ratio * self.contract_id.motivation / self.company_id.motivation_ratio
            vals = {
                'input_type_id': self.env.ref('hr_payroll_summary.input_motivation').id,
                'name': 'Motivation',
                'code': 'MOTIVATION',
                'amount': amount,
            }
            res.append((0, 0, vals))
            # Efforts
            amount = summary_line.effort_ratio * self.contract_id.efforts / self.company_id.effort_ratio

            vals = {
                'input_type_id': self.env.ref('hr_payroll_summary.input_efforts').id,
                'name': 'Efforts',
                'code': 'EFFORTS',
                'amount': amount,
            }
            res.append((0, 0, vals))

        return res
