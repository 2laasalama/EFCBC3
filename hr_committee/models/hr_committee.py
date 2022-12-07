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


class HrCommittee(models.Model):
    _name = "hr.committee"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Committee"
    _order = "id desc"

    @api.model
    def _default_date_range(self):
        today = fields.Date.context_today(self)
        range = self.env['date.range'].search([('date_start', '<=', today), ('date_end', '>=', today)], limit=1)
        return range.id if range else False

    name = fields.Char(required=True, default='New', readonly=True, states={"draft": [("readonly", False)]})

    date_range_id = fields.Many2one("date.range", required=True, string="الفترة", default=_default_date_range,
                                    states={"draft": [("readonly", False)]})
    type_id = fields.Many2one("date.range.type", required=True, string="السنة", related='date_range_id.type_id')
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    date = fields.Date(default=fields.Date.context_today)
    month_ar = fields.Char(compute='_compute_month_ar', string='الشهر')
    line_ids = fields.One2many("hr.committee.line", "committee_id", string="Lines", readonly=True,
                               states={"draft": [("readonly", False)]})
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], string="Status", index=True,
                             readonly=True, copy=False, tracking=1, default="draft", )
    vice_hr_manager = fields.Many2one('hr.employee', string='نائب رئيس الأمانة التنفيذية للموارد البشرية')
    vice_hr_manager_title = fields.Char(default='أستاذة')

    hr_consultant = fields.Many2one('hr.employee', string='مستشار (أ) للموارد البشرية')
    hr_consultant_title = fields.Char(default='محاسب')

    hr_manager = fields.Many2one('hr.employee', string='رئيس الأمانة التنفيذية للموارد البشرية')
    hr_manager_title = fields.Char(default='محاسب')

    general_secretary = fields.Many2one('hr.employee', string='الامين العام')
    general_secretary_title = fields.Char(default='محاسب')

    total_earnings = fields.Float(compute='_compute_total_earnings')
    total_taxes = fields.Float(compute='_compute_total_taxes')
    total_net_pay = fields.Float(compute='_compute_total_net_pay')

    @api.depends('line_ids', 'line_ids.net_pay')
    def _compute_total_net_pay(self):
        for rec in self:
            rec.total_net_pay = sum(line.net_pay for line in rec.line_ids)

    @api.depends('line_ids', 'line_ids.taxes')
    def _compute_total_taxes(self):
        for rec in self:
            rec.total_taxes = sum(line.taxes for line in rec.line_ids)

    @api.depends('line_ids', 'line_ids.total_earnings')
    def _compute_total_earnings(self):
        for rec in self:
            rec.total_earnings = sum(line.total_earnings for line in rec.line_ids)

    @api.depends('date_from')
    def _compute_month_ar(self):
        for rec in self:
            rec.month_ar = ''
            month = rec.date_from.month
            months = dict(MONTHS)
            rec.month_ar = months[month]

    def print_report(self):
        return self.env.ref('hr_committee.committee_report').report_action(self.id)

    def draft_committee(self):
        return self.write({"state": "draft"})

    def close_committee(self):
        return self.write({"state": "close"})

    def done_committee(self):
        return self.write({"state": "done"})

    def compute_sheet(self):
        for rec in self:
            self.line_ids.compute_sheet()
