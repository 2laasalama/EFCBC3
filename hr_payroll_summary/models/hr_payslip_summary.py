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
    date_range_id = fields.Many2one("date.range", required=True, string="Period",
                                    states={"draft": [("readonly", False)]})
    date_from = fields.Date(string="Date From", required=True,
                            related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')

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
