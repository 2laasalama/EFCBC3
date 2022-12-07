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
        })
        return res
