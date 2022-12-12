from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from pytz import timezone, UTC

MONTHS = [(1, 'يناير'),
          (2, 'فبراير'),
          (3, 'مارس'),
          (4, 'إبريل'),
          (5, 'مايو'),
          (6, 'يونيو'),
          (7, 'يوليو'),
          (8, 'أغسطس'),
          (9, 'سبتمبر'),
          (10, 'أكتوبر'),
          (11, 'نوفمبر'),
          (12, 'ديسمبر')]


class EmployeePerformance(models.Model):
    _name = "hr.employee.performance.line"
    _inherit = 'hr.payslip.summary.line'
    _description = "Employee Performance Line"

    performance_id = fields.Many2one('hr.employee.performance')
    month_ar = fields.Char(compute='_compute_month_ar', string='الشهر')
    public_holidays = fields.Float(compute='_compute_public_holidays', )
    total_permissions = fields.Float(compute='_compute_total_permissions')
    total_missions = fields.Float(compute='_compute_total_missions')

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_total_missions(self):
        for rec in self:
            domain = [('leave_category', '=', 'mission')]
            rec.total_missions = rec.employee_id.get_leaves_summary(rec.date_from, rec.date_to, domain)

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_total_permissions(self):
        for rec in self:
            domain = [('leave_category', '=', 'permission')]
            rec.total_permissions = rec.employee_id.get_leaves_summary(rec.date_from, rec.date_to, domain)

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_public_holidays(self):
        for rec in self:
            rec.public_holidays = rec.employee_id.get_public_leaves_summary(rec.date_from, rec.date_to)

    @api.depends('date_from')
    def _compute_month_ar(self):
        for rec in self:
            rec.month_ar = ''
            month = rec.date_from.month
            months = dict(MONTHS)
            rec.month_ar = months[month]

    def get_annual_leaves(self):
        vals = []
        for leave_type in self.env['hr.leave.type'].search([('leave_category', '=', 'annual')]):
            domain = [('holiday_status_id', '=', leave_type.id)]
            leaves_count = self.employee_id.get_leaves_summary(self.date_from, self.date_to, domain)
            vals.append({
                'number_of_days': leaves_count,
            })

        return vals

    def get_other_leaves(self):
        vals = []
        for leave_type in self.env['hr.leave.type'].search([('leave_category', '=', 'other')]):
            domain = [('holiday_status_id', '=', leave_type.id)]
            leaves_count = self.employee_id.get_leaves_summary(self.date_from, self.date_to, domain)

            vals.append({
                'number_of_days': leaves_count,
            })

        return vals
