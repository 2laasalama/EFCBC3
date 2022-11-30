from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmployeePerformance(models.Model):
    _name = "hr.employee.performance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Employee Performance"
    _order = "id desc"

    name = fields.Char(compute="_compute_name")
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    year_id = fields.Many2one("date.range.type", required=True, string="Year")
    company_id = fields.Many2one("res.company", string="Company", required=True, copy=False,
                                 default=lambda self: self.env.company, )

    state = fields.Selection([("draft", "Draft"), ("close", "Close")], string="Status", index=True, readonly=True,
                             copy=False, tracking=1, default="draft")

    line_ids = fields.One2many("hr.employee.performance.line", "performance_id", string="Lines", readonly=True,
                               states={"draft": [("readonly", False)]})
    total_public_holidays = fields.Float(compute='_compute_total_public_holidays', )

    @api.depends('employee_id', 'year_id')
    def _compute_name(self):
        for rec in self:
            rec.name = "{} - {}".format(rec.employee_id.name, rec.year_id.name)

    @api.depends('line_ids', 'line_ids.public_holidays')
    def _compute_total_public_holidays(self):
        for rec in self:
            rec.total_public_holidays = sum(line.public_holidays for line in rec.line_ids)

    def print_report(self):
        return self.env.ref('hr_payroll_summary.employee_performance_report').report_action(self.id)

    def get_annual_leaves(self):
        return self.env['hr.leave.type'].search([('leave_category', '=', 'annual')])

    def get_other_leaves(self):
        return self.env['hr.leave.type'].search([('leave_category', '=', 'other')])

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "Name must be unique!",
        )
    ]

    def draft_employee_performance(self):
        return self.write({"state": "draft"})

    def close_employee_performance(self):
        return self.write({"state": "close"})

    def compute_sheet(self):
        for rec in self:
            lines = self.env["hr.employee.performance.line"]
            rec.line_ids.unlink()
            sequence = 0
            for date_range_id in rec.year_id.date_range_ids:
                sequence += 1
                res = {
                    "sequence": sequence,
                    "employee_id": rec.employee_id.id,
                    "performance_id": rec.id,
                    "date_range_id": date_range_id.id,
                }
                lines += self.env["hr.employee.performance.line"].create(res)
            lines.compute_sheet()
