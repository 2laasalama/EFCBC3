from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrPayslipsummary(models.Model):
    _name = "hr.payslip.summary"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Payslip Summary"
    _order = "id desc"

    name = fields.Char(required=True, default='New', readonly=True, states={"draft": [("readonly", False)]})
    line_ids = fields.One2many("hr.payslip.summary.line", "summary_id", string="Lines", readonly=True,
                               states={"draft": [("readonly", False)]})
    state = fields.Selection([("draft", "Draft"), ("close", "Close")], string="Status", index=True, readonly=True,
                             copy=False, tracking=1, default="draft", )
    company_id = fields.Many2one("res.company", string="Company", required=True, copy=False,
                                 default=lambda self: self.env.company, )
    date_range_id = fields.Many2one("date.range", required=True, string="الفترة",
                                    states={"draft": [("readonly", False)]})
    date_from = fields.Date(string="Date From", required=True,
                            related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    motivation_ratio = fields.Float(related='company_id.motivation_ratio', string='نسبة الحافز', readonly=True)
    effort_ratio = fields.Float(related='company_id.effort_ratio', string='نسبة الجهود', readonly=True)
    personnel_affairs_unit = fields.Many2one('hr.employee', string='وحدة شئون العاملين')
    personnel_affairs_unit_title = fields.Char(default='محاسب')
    vice_hr_manager = fields.Many2one('hr.employee', string='نائب رئيس الأمانة التنفيذية للموارد البشرية')
    vice_hr_manager_title = fields.Char(default='أستاذة')
    hr_manager = fields.Many2one('hr.employee', string='رئيس الأمانة التنفيذية للموارد البشرية')
    hr_manager_title = fields.Char(default='محاسب')
    general_secretary = fields.Many2one('hr.employee', string='الامين العام')
    general_secretary_title = fields.Char(default='محاسب')

    def print_report(self):
        return self.env.ref('hr_payroll_summary.payslip_summary_report').report_action(self.id)

    def get_leave_types(self):
        return self.env['hr.leave.type'].search([('payroll_summary', '=', True)])

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "Name must be unique!",
        )
    ]

    def draft_payslip_summary(self):
        return self.write({"state": "draft"})

    def close_payslip_summary(self):
        return self.write({"state": "close"})

    def compute_sheet(self):
        for rec in self:
            self.line_ids.compute_sheet()
