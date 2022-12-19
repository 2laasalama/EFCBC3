from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

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


class QuarterIncentive(models.Model):
    _name = "hr.quarter.incentive"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Quarter Incentive"
    _order = "id desc"

    @api.model
    def _default_date_range(self):
        today = fields.Date.context_today(self)
        range = self.env['date.range'].search([('date_start', '<=', today), ('date_end', '>=', today)], limit=1)
        return range.id if range else False

    name = fields.Char(required=True, default='كشف حافز ربع سنوى', readonly=True,
                       states={"draft": [("readonly", False)]})

    date_range_id = fields.Many2one("date.range", required=True, string="الفترة", default=_default_date_range,
                                    states={"draft": [("readonly", False)]})
    type_id = fields.Many2one("date.range.type", required=True, string="السنة", related='date_range_id.type_id')
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    date = fields.Date(default=fields.Date.context_today)
    month_ar = fields.Char(compute='_compute_month_ar', string='الشهر')

    first_month = fields.Char(compute='_compute_month_ar')
    second_month = fields.Char(compute='_compute_second_month')
    third_month = fields.Char(compute='_compute_third_month')

    line_ids = fields.One2many("hr.quarter.incentive.line", "allowance_id", readonly=False)
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

    def get_month_string(self, date_from):
        month = date_from.month
        months = dict(MONTHS)
        return months[month]

    @api.depends('date_from')
    def _compute_month_ar(self):
        for rec in self:
            rec.month_ar = rec.first_month = rec.get_month_string(rec.date_from)

    @api.depends('date_from')
    def _compute_second_month(self):
        for rec in self:
            rec.second_month = rec.get_month_string(rec.date_from - relativedelta(months=1))

    @api.depends('date_from')
    def _compute_third_month(self):
        for rec in self:
            rec.third_month = rec.get_month_string(rec.date_from - relativedelta(months=2))

    def print_report(self):
        return self.env.ref('hr_salary_attachment.quarter_incentive_report').report_action(self.id)

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
                self.env["hr.quarter.incentive.line"].create(res)
            rec.line_ids.compute_months_amount()

    def update_sheet(self):
        for rec in self:
            rec.line_ids.compute_months_amount()


class QuarterIncentiveLine(models.Model):
    _name = "hr.quarter.incentive.line"

    allowance_id = fields.Many2one('hr.quarter.incentive')
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], related='allowance_id.state')

    date_range_id = fields.Many2one("date.range", related='allowance_id.date_range_id', required=True,
                                    string="Period")
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    sequence = fields.Integer(readonly=True, default=1)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True, required=True)
    employee_code = fields.Char(related='employee_id.code', string="Code")

    contract_id = fields.Many2one('hr.contract', string='Contract', compute='_compute_contract_id')

    company_id = fields.Many2one("res.company", string="Company", required=True, copy=False,
                                 default=lambda self: self.env.company, )

    first_month = fields.Float(readonly=True)
    second_month = fields.Float(readonly=True)
    third_month = fields.Float(readonly=True)

    total_months = fields.Float(compute='_compute_total_months')
    taxes = fields.Float(compute='_compute_totals')
    net = fields.Float(compute='_compute_totals')
    print = fields.Boolean(default=True)

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_contract_id(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date_from, rec.date_to)
            rec.contract_id = False
            if contracts:
                rec.contract_id = contracts[0]

    @api.depends('first_month', 'second_month', 'third_month')
    def _compute_total_months(self):
        for rec in self:
            rec.total_months = rec.first_month + rec.second_month + rec.third_month

    @api.depends('total_months')
    def _compute_totals(self):
        for rec in self:
            tax_ratio = self.env['ir.config_parameter'].sudo().get_param('efcbc_cutome_hr.tax_ratio')
            rec.taxes = rec.total_months * float(tax_ratio) / 100
            rec.net = rec.total_months - rec.taxes

    def get_motivation_ratio(self, employee_id, date_range_id):
        if employee_id._get_contracts(date_range_id.date_start, date_range_id.date_end):
            line = self.env["hr.payslip.summary.line"].new({
                "employee_id": employee_id.id,
                "date_range_id": date_range_id.id,
            })
            line.compute_sheet()
            motivation_effort_days = (30 - line.motivation_effort_days) / 30
            motivation_ratio = motivation_effort_days * line.motivation_ratio / self.company_id.motivation_ratio
            return motivation_ratio / 3
        else:
            return 0

    def compute_month_amount(self, date_range_id):
        motivation_ratio = self.get_motivation_ratio(self.employee_id, date_range_id)
        amount = motivation_ratio * self.contract_id.motivation
        return amount

    def compute_months_amount(self):
        for rec in self:
            # first_month
            rec.first_month = rec.compute_month_amount(rec.date_range_id)

            # second_month
            date_from = rec.date_from - relativedelta(months=1)
            date_range_id = self.env['date.range'].search(
                [('date_start', '<=', date_from), ('date_end', '>=', date_from)], limit=1)
            if date_range_id:
                rec.second_month = rec.compute_month_amount(date_range_id)

            # third_month
            date_from = rec.date_from - relativedelta(months=2)
            date_range_id = self.env['date.range'].search(
                [('date_start', '<=', date_from), ('date_end', '>=', date_from)], limit=1)
            if date_range_id:
                rec.third_month = rec.compute_month_amount(date_range_id)
