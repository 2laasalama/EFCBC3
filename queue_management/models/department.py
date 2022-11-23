# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _

import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DepartmentDepartment(models.Model):
    _name = 'department.department'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Department"
    _order = 'ref'

    name = fields.Char("Department")
    ref = fields.Integer(readonly=True)
    capacity = fields.Integer(default=30)
    exception_ids = fields.One2many('capacity.exception', 'department_id')
    token_ids = fields.One2many('token.token', 'token_dept')
    available_tickets_today = fields.Integer(compute='_compute_available_tickets_today')

    @api.depends('token_ids', 'capacity', 'exception_ids')
    def _compute_available_tickets_today(self):
        for rec in self:
            today = fields.Date.today()
            rec.available_tickets_today = rec.get_available_tickets(today)

    def get_available_tickets(self, date):
        all_tickets = len(self.token_ids.filtered(lambda t: t.date == date and t.state != 'cancel'))
        exception = self.exception_ids.filtered(lambda t: t.date == date)
        capacity = exception.capacity if exception else self.capacity
        available_tickets = capacity - all_tickets
        return available_tickets


class CapacityException(models.Model):
    _name = 'capacity.exception'

    department_id = fields.Many2one('department.department')
    date = fields.Date()
    capacity = fields.Integer(default=30)

    _sql_constraints = [
        ('date_department_uid_unique', 'unique (department_id, date)',
         'Sorry, You Can not define more than one exception per day'),
    ]

    @api.constrains('department_id', 'date')
    def _check_payment_number_constraint(self):
        for rec in self.filtered(lambda p: p.date):
            domain = [('id', '!=', rec.id), ('date', '=', rec.date), ('department_id', '=', rec.department_id.id)]
            if self.search(domain):
                raise ValidationError(_("Sorry, You Can not define more than one exception per day"))
