# -*- coding: utf-8 -*-
import babel
import time
from datetime import datetime

from odoo import models, Command, fields, api, tools, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        self.input_line_ids = self.get_input_lines(self.date_from, self.date_to)

    def get_input_lines(self, date_from, date_to):
        return []
