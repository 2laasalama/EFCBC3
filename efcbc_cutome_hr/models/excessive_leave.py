# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ExcessiveLeave(models.Model):
    _name = 'excessive.leave'
    _description = 'Excessive Leave'

    date_from = fields.Date(
        string='From', required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(
        string='To', required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    excessive_lines = fields.One2many('excessive.leave.line', 'excessive_id')

    def action_apply(self):
        self.excessive_lines = False
        for employee in self.env['hr.employee'].search([]):
            leaves = self.env['hr.leave'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'validate'),
                ('exclude_penalty', '=', False)
            ])
            leaves_in = leaves.filtered(lambda l: l.date_from.date() < self.date_to
                                                  and self.date_from <= l.date_to.date() < self.date_to)
            number_of_days = sum(leaves_in.mapped('number_of_days'))
            rule = False
            if number_of_days > 0:
                rule = self.env['excessive.leave.policy'].check_deduction_rule(number_of_days)
            self.env['excessive.leave.line'].create({
                'excessive_id': self.id,
                'employee_id': employee.id,
                'number_of_days': number_of_days,
                'deduction_name': rule.name if rule else False,
                'deduction': rule.deduction if rule else False,
            })

    @api.depends('date_from', 'date_to')
    def name_get(self):
        res = []
        for rec in self:
            name = "{} - {}".format(rec.date_from, rec.date_to)
            res.append((rec.id, name))
        return res


class ExcessiveLeaveLine(models.Model):
    _name = 'excessive.leave.line'
    _description = 'Excessive Leave Line'

    excessive_id = fields.Many2one('excessive.leave')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    number_of_days = fields.Float('Number of Days Taken')
    deduction_name = fields.Char('Name of Rule')
    deduction = fields.Float('Deduction (%)')
