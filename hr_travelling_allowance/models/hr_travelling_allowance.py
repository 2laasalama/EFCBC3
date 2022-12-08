# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrTravellingAllowance(models.Model):
    _name = "hr.travelling.allowance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Travelling Allowance"

    name = fields.Char(required=True, default='New', readonly=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    employee_code = fields.Char(related='employee_id.code', string="Employee Code")
    grade_id = fields.Many2one('employee.grade', related='employee_id.grade_id', string='Employee Grade')
    type_id = fields.Many2one('hr.mission.type', 'Mission Type', required=True)
    line_ids = fields.One2many("hr.travelling.allowance.line", "allowance_id", string="Lines", readonly=True,
                               states={"draft": [("readonly", False)]})
    expenses_ids = fields.One2many("hr.travelling.expenses", "allowance_id", string="Expenses", readonly=True,
                                   states={"draft": [("readonly", False)]})
    other_expenses_ids = fields.One2many("hr.other.expenses", "allowance_id", string="Other Expenses", readonly=True,
                                         states={"draft": [("readonly", False)]})
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], string="Status", index=True,
                             readonly=True,
                             copy=False, tracking=1, default="draft", )
    vice_hr_manager = fields.Many2one('hr.employee', string='نائب رئيس الأمانة التنفيذية للموارد البشرية')
    vice_hr_manager_title = fields.Char(default='أستاذة')

    hr_consultant = fields.Many2one('hr.employee', string='مستشار (أ) للموارد البشرية')
    hr_consultant_title = fields.Char(default='محاسب')

    hr_manager = fields.Many2one('hr.employee', string='رئيس الأمانة التنفيذية للموارد البشرية')
    hr_manager_title = fields.Char(default='محاسب')

    general_secretary = fields.Many2one('hr.employee', string='الامين العام')
    general_secretary_title = fields.Char(default='محاسب')

    total_amount = fields.Float(compute='_compute_total_amount')

    @api.depends('line_ids', 'expenses_ids', 'other_expenses_ids')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(l.total_amount for l in rec.line_ids) + \
                               sum(l.total_amount for l in rec.expenses_ids) + \
                               sum(l.total_amount for l in rec.other_expenses_ids)

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.travelling.allowance') or _('New')
        return super(HrTravellingAllowance, self).create(vals)

    def print_report(self):
        return
        # return self.env.ref('hr_travelling_allowance.medical_claims_report').report_action(self.id)

    def draft_action(self):
        return self.write({"state": "draft"})

    def close_action(self):
        return self.write({"state": "close"})

    def done_action(self):
        return self.write({"state": "done"})


class HrTravellingAllowanceLine(models.Model):
    _name = "hr.travelling.allowance.line"

    allowance_id = fields.Many2one('hr.travelling.allowance')
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    status = fields.Char()
    number_of_days = fields.Integer(compute='_compute_number_of_days', required=True)
    amount_of_day = fields.Float(required=True)
    total_amount = fields.Float(compute='_compute_total_amount')

    @api.depends('number_of_days', 'amount_of_day')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.number_of_days * rec.amount_of_day

    @api.depends('date_from', 'date_to')
    def _compute_number_of_days(self):
        for rec in self:
            rec.number_of_days = 0
            if rec.date_to and rec.date_from:
                rec.number_of_days = (rec.date_to - rec.date_from).days


class HrTravellingExpenses(models.Model):
    _name = "hr.travelling.expenses"

    allowance_id = fields.Many2one('hr.travelling.allowance')
    date = fields.Date(default=fields.Date.context_today, required=True)
    location_from = fields.Many2one('hr.travelling.location', required=True)
    location_to = fields.Many2one('hr.travelling.location', required=True)
    total_amount = fields.Float(compute='_compute_total_amount')

    @api.depends('location_from', 'location_to')
    def _compute_total_amount(self):
        for rec in self:
            route = self.env['hr.travelling.route'].search(
                [('location_from', '=', rec.location_from.id), ('location_to', '=', rec.location_to.id)], limit=1)
            if not route:
                route = self.env['hr.travelling.route'].search(
                    [('location_from', '=', rec.location_to.id), ('location_to', '=', rec.location_from.id)], limit=1)
            rec.total_amount = 0
            if route:
                rec.total_amount = route.amount


class HrOtherExpenses(models.Model):
    _name = "hr.other.expenses"

    allowance_id = fields.Many2one('hr.travelling.allowance')
    notes = fields.Char()
    date = fields.Date(default=fields.Date.context_today, required=True)
    location_from = fields.Many2one('hr.travelling.location')
    location_to = fields.Many2one('hr.travelling.location')
    type = fields.Char()
    total_amount = fields.Float(required=True)


class MissionType(models.Model):
    _name = "hr.mission.type"

    name = fields.Char(required=True)
