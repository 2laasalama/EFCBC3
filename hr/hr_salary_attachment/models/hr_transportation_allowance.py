from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

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


class HrTransportationAllowance(models.Model):
    _name = "hr.transportation.allowance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Transportation Allowance"
    _order = "id desc"

    @api.model
    def _default_date_range(self):
        today = fields.Date.context_today(self)
        range = self.env['date.range'].search([('date_start', '<=', today), ('date_end', '>=', today)], limit=1)
        return range.id if range else False

    name = fields.Char(required=True, default='كشف بدل الانتقال', readonly=True,
                       states={"draft": [("readonly", False)]})

    date_range_id = fields.Many2one("date.range", required=True, string="الفترة", default=_default_date_range,
                                    states={"draft": [("readonly", False)]})
    type_id = fields.Many2one("date.range.type", required=True, string="السنة", related='date_range_id.type_id')
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    date = fields.Date(default=fields.Date.context_today)
    month_ar = fields.Char(compute='_compute_month_ar', string='الشهر')

    line_ids = fields.One2many("hr.transportation.allowance.line", "allowance_id", readonly=False)
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

    @api.depends('date_from')
    def _compute_month_ar(self):
        for rec in self:
            rec.month_ar = ''
            month = rec.date_from.month
            months = dict(MONTHS)
            rec.month_ar = months[month]

    def print_report(self):
        return self.env.ref('hr_salary_attachment.transportation_allowance_report').report_action(self.id)

    def draft_action(self):
        return self.write({"state": "draft"})

    def close_action(self):
        return self.write({"state": "close"})

    def done_action(self):
        return self.write({"state": "done"})

    def compute_sheet(self):
        for rec in self:
            rec.line_ids.unlink()
            for employee in self.env['hr.employee'].search([]):
                res = {
                    "allowance_id": rec.id,
                    "employee_id": employee.id,
                    "date_range_id": rec.date_range_id.id,
                }
                self.env["hr.transportation.allowance.line"].create(res)

    def get_leave_types(self):
        return self.env['hr.leave.type'].search([('leave_category', 'in', ['annual', 'other'])], order='leave_category')


class HrTransportationAllowanceLine(models.Model):
    _name = "hr.transportation.allowance.line"

    allowance_id = fields.Many2one('hr.transportation.allowance')
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], related='allowance_id.state')
    date_range_id = fields.Many2one("date.range", related='allowance_id.date_range_id', required=True,
                                    string="Period")
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    sequence = fields.Integer(readonly=True, default=1)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True, required=True)
    employee_code = fields.Char(related='employee_id.code', string="Code")
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='compute_required_data')
    number_of_days = fields.Integer(default=20, readonly=True)
    transportation_allowance = fields.Float(string="Transportation Allowance",
                                            related='contract_id.transportation_allowance')
    amount_of_day = fields.Float(compute='_compute_amount_of_day')
    total_absence = fields.Float(compute='_compute_total_absence')
    total_leaves = fields.Float(compute='_compute_total_leaves')
    total_deduction = fields.Float(compute='_compute_totals')
    net = fields.Float(compute='_compute_totals')
    print = fields.Boolean(default=True)

    @api.depends('number_of_days', 'transportation_allowance')
    def _compute_amount_of_day(self):
        for rec in self:
            rec.amount_of_day = rec.transportation_allowance / rec.number_of_days

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_total_absence(self):
        for rec in self:
            line = self.env["hr.payslip.summary.line"].new({
                "employee_id": rec.employee_id.id,
                "date_range_id": rec.date_range_id.id,
            })
            if rec.employee_id._get_contracts(rec.date_from, rec.date_to):
                line.compute_sheet()
            rec.total_absence = line.motivation_effort_days

    @api.depends('total_absence', 'employee_id', 'date_from')
    def _compute_total_leaves(self):
        for rec in self:
            domain = [('leave_category', 'in', ['annual', 'other'])]
            total_leaves = rec.employee_id.get_leaves_summary(rec.date_from, rec.date_to, domain)
            rec.total_leaves = total_leaves + rec.total_absence

    @api.depends('amount_of_day', 'total_leaves')
    def _compute_totals(self):
        for rec in self:
            rec.total_deduction = rec.total_leaves * rec.amount_of_day
            net = rec.transportation_allowance - rec.total_deduction
            rec.net = net if net > 0 else 0

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_required_data(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date_from, rec.date_to)
            rec.contract_id = False
            if contracts:
                rec.contract_id = contracts[0]

    def get_leave_summary(self):
        for rec in self:
            vals = []

            for leave_type in self.env['hr.leave.type'].search([('leave_category', 'in', ['annual', 'other'])],
                                                               order='leave_category'):
                domain = [('holiday_status_id', '=', leave_type.id)]

                leaves_count = self.employee_id.get_leaves_summary(rec.date_from, rec.date_to, domain)

                vals.append({
                    'number_of_days': leaves_count,
                })

            return vals
