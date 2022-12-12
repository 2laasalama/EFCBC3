from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrPayslipsummaryLeave(models.Model):
    _name = "hr.payslip.summary.leave"

    name = fields.Char(compute='_compute_name')
    summary_line_id = fields.Many2one('hr.payslip.summary.line')
    holiday_status_id = fields.Many2one('hr.leave.type', 'Leave Type', required=True)
    number_of_days = fields.Integer(default='0')

    @api.depends('holiday_status_id', 'number_of_days')
    def _compute_name(self):
        for rec in self:
            rec.name = "{} - {} Days".format(rec.holiday_status_id.name, rec.number_of_days)
