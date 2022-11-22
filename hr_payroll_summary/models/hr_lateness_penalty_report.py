from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrLatenessPenaltyReport(models.Model):
    _name = "hr.lateness.penalty.report"
    _order = 'date_from'

    summary_line_id = fields.Many2one('hr.payslip.summary.line')
    name = fields.Char(compute='_compute_name')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    att_policy_id = fields.Many2one('hr.attendance.policy', string="Attendance Policy")
    date_range_id = fields.Many2one("date.range", required=True, string="Period")
    date_from = fields.Date(string="Date From", required=False, related='date_range_id.date_start', store=True)
    date_to = fields.Date(string="Date To", required=False, related='date_range_id.date_end', store=True)
    total_lateness = fields.Float()
    allowed_lateness = fields.Float(compute='_compute_penalty')
    absence_days = fields.Float(compute='_compute_penalty')
    rule_id = fields.Many2one('lateness.penalty', store=True, compute='_compute_penalty')
    sequence = fields.Integer(compute='_compute_penalty')
    written_warning = fields.Boolean(compute='_compute_penalty')
    hs_penalty = fields.Boolean(compute='_compute_hs_penalty')
    penalty_value = fields.Float(compute='_compute_penalty_value')

    @api.depends('employee_id', 'date_range_id')
    def _compute_name(self):
        for rec in self:
            rec.name = "{} - {}".format(rec.employee_id.name, rec.date_range_id.name)

    @api.depends('rule_id', 'sequence')
    def _compute_penalty_value(self):
        for rec in self:
            rec.penalty_value = False
            if rec.sequence > 0 and rec.rule_id:
                if rec.sequence == 1:
                    rec.penalty_value = rec.rule_id.first
                if rec.sequence == 2:
                    rec.penalty_value = rec.rule_id.second
                if rec.sequence == 3:
                    rec.penalty_value = rec.rule_id.third
                if rec.sequence > 3:
                    rec.penalty_value = rec.rule_id.fourth

    @api.depends('rule_id', 'written_warning')
    def _compute_hs_penalty(self):
        for rec in self:
            rec.hs_penalty = True if rec.rule_id or rec.written_warning else False

    def get_rule(self, lateness_minutes):
        old_penalty = self.search_count([('employee_id', '=', self.employee_id.id),
                                         ('date_from', '<', self.date_from)])
        rule = False
        if old_penalty < 1:
            self.written_warning = True
            # if lateness_minutes <= self.att_policy_id.written_warning:
            #     rule = self.att_policy_id.lateness_penalty_ids.filtered(
            #         lambda l: l.from_time <= lateness_minutes <= l.to_time)
            lateness_minutes -= self.att_policy_id.written_warning

        if lateness_minutes > 0:
            rule = self.att_policy_id.lateness_penalty_ids.filtered(
                lambda l: l.from_time <= lateness_minutes <= l.to_time)

        self.rule_id = rule

    def get_penalty_sequence(self):
        sequence = 0
        if self.rule_id:
            lateness_penalty_month = self.att_policy_id.lateness_penalty_month - 1
            start_date = self.date_from + relativedelta(months=-lateness_penalty_month)
            penalties = self.search([('employee_id', '=', self.employee_id.id),
                                     ('rule_id', '=', self.rule_id.id),
                                     ('date_from', '>=', start_date),
                                     ], order='date_from')

            for penalty in penalties:
                sequence += 1
                if self.id == penalty.id:
                    break
        return sequence

    @api.depends('employee_id', 'date_from', 'total_lateness')
    def _compute_penalty(self):
        for rec in self:
            rec.rule_id = rec.written_warning = rec.absence_days = rec.sequence = False
            rec.allowed_lateness = rec.att_policy_id.late_rule_id.allowed_lateness
            if rec.total_lateness > rec.allowed_lateness:
                rec.absence_days = int(rec.total_lateness - rec.allowed_lateness)
                lateness_minutes = (rec.total_lateness - rec.absence_days - rec.allowed_lateness)
                if lateness_minutes > 0:
                    rec.get_rule(lateness_minutes)
                rec.sequence = rec.get_penalty_sequence()
