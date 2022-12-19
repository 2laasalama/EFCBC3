# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HREmployeeRewards(models.Model):
    _name = "hr.employee.rewards"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Employee Rewards"

    @api.model
    def _default_date_range(self):
        today = fields.Date.context_today(self)
        range = self.env['date.range'].search([('date_start', '<=', today), ('date_end', '>=', today)], limit=1)
        return range.id if range else False

    name = fields.Char(required=True, readonly=True, states={"draft": [("readonly", False)]})
    date_range_id = fields.Many2one("date.range", required=True, string="Period", default=_default_date_range,
                                    states={"draft": [("readonly", False)]})
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    line_ids = fields.One2many("hr.employee.rewards.line", "rewards_id", string="Lines", readonly=True,
                               states={"draft": [("readonly", False)]})
    mode = fields.Selection([("amount", "Amount"), ("percentage", "Percentage"), ("different", "Different Amounts")],
                            readonly=True, required=True, states={"draft": [("readonly", False)]}, default="amount", )
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], string="Status", index=True,
                             readonly=True, copy=False, tracking=1, default="draft", )
    amount = fields.Float()
    percentage = fields.Float()

    vice_hr_manager = fields.Many2one('hr.employee', string='نائب رئيس الأمانة التنفيذية للموارد البشرية')
    vice_hr_manager_title = fields.Char(default='أستاذة')

    hr_consultant = fields.Many2one('hr.employee', string='مستشار (أ) للموارد البشرية')
    hr_consultant_title = fields.Char(default='محاسب')

    hr_manager = fields.Many2one('hr.employee', string='رئيس الأمانة التنفيذية للموارد البشرية')
    hr_manager_title = fields.Char(default='محاسب')

    general_secretary = fields.Many2one('hr.employee', string='الامين العام')
    general_secretary_title = fields.Char(default='محاسب')

    def print_report(self):
        return
        # return self.env.ref('hr_travelling_allowance.medical_claims_report').report_action(self.id)

    def draft_action(self):
        return self.write({"state": "draft"})

    def close_action(self):
        return self.write({"state": "close"})

    def done_action(self):
        return self.write({"state": "done"})


class HREmployeeRewardsLine(models.Model):
    _name = "hr.employee.rewards.line"

    rewards_id = fields.Many2one('hr.employee.rewards')
    mode = fields.Selection([("amount", "Amount"), ("percentage", "Percentage"), ("different", "Different Amounts")],
                            related='rewards_id.mode')
    date_range_id = fields.Many2one("date.range", required=True, string="Period", related='rewards_id.date_range_id')
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='_compute_contract_id')
    amount = fields.Float(related='rewards_id.amount')
    percentage = fields.Float(related='rewards_id.percentage')
    free_total_amount = fields.Float(string='Total Amount')
    total_amount = fields.Float(compute='_compute_total_amount')

    @api.onchange('mode', 'rewards_id.mode')
    def onchange_mode(self):
        self.free_total_amount = 0.0

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_contract_id(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date_from, rec.date_to)
            rec.contract_id = False
            if contracts:
                rec.contract_id = contracts[0]

    @api.depends('mode', 'amount', 'percentage', 'free_total_amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = 0
            if rec.mode == 'amount':
                rec.total_amount = rec.amount
            elif rec.mode == 'percentage' and rec.contract_id:
                rec.total_amount = (rec.contract_id.basic_salary + rec.contract_id.variable_salary) * rec.percentage
            elif rec.mode == 'different':
                rec.total_amount = rec.free_total_amount

    @api.constrains('employee_id', 'mode', 'date_from', 'date_to')
    def check_percentage_type(self):
        for rec in self:
            if rec.mode == 'percentage' and not rec.contract_id:
                raise ValidationError(_('There is no valid contract for employee %s in period [%s - %s]' % (
                    rec.employee_id.name, rec.date_from, rec.date_to)))

    @api.depends('date_from', 'date_to')
    def _compute_number_of_days(self):
        for rec in self:
            rec.number_of_days = 0
            if rec.date_to and rec.date_from:
                rec.number_of_days = (rec.date_to - rec.date_from).days
