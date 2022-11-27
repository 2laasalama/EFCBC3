# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ExcessiveLeave(models.Model):
    _name = 'excessive.leave'
    _description = 'Excessive Leave'

    date_range_id = fields.Many2one("date.range", required=True, string="Period")
    date_from = fields.Date(string="Date From", required=False, related='date_range_id.date_start', store=True)
    date_to = fields.Date(string="Date To", required=False, related='date_range_id.date_end', store=True)
    excessive_lines = fields.One2many('excessive.leave.line', 'excessive_id')

    def action_apply(self):
        self.excessive_lines.unlink()
        for employee in self.env['hr.employee'].search([]):
            line = self.env['excessive.leave.line'].create({
                'excessive_id': self.id,
                'employee_id': employee.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
            line.action_update()

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
    date_from = fields.Date()
    date_to = fields.Date()
    employee_id = fields.Many2one('hr.employee', string='Employee')
    number_of_days = fields.Float('Number of Days Taken')
    deduction_name = fields.Char('Name of Rule')
    deduction = fields.Float('Deduction (%)')

    def action_update(self):
        for rec in self:

            start_dt = datetime.combine(rec.date_from, datetime.min.time())
            end_dt = datetime.combine(rec.date_to, datetime.min.time())
            left = rec.employee_id.sudo()._get_leave_days_data_batch(start_dt, end_dt,
                                                                     domain=[('time_type', '=', 'leave')])[
                rec.employee_id.id]['days']

            if left > 0:
                rule = self.env['excessive.leave.policy'].check_deduction_rule(left)
                rec.update({
                    'number_of_days': left,
                    'deduction_name': rule.name,
                    'deduction': rule.deduction,
                })
