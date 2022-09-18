# -*- coding: utf-8 -*-

from odoo import models, fields


class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    committee_type = fields.Selection(
        string='نوع االلجنة',
        selection=[('bid_opening', 'فتح مظاريف'),
                   ('technical', 'فنية'),
                   ('financial', 'مالية'),
                   ('decision', 'بت')])

class Employee(models.Model):
    _inherit = 'hr.employee'

    committee_type = fields.Selection(
        string='نوع االلجنة',
        selection=[('bid_opening', 'فتح مظاريف'),
                   ('technical', 'فنية'),
                   ('financial', 'مالية'),
                   ('decision', 'بت')])
