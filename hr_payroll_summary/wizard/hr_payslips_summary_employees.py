from odoo import _, fields, models
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _name = "hr.payslip.summary.employees"
    _description = "Generate payslips summary for all selected employees"

    employee_ids = fields.Many2many("hr.employee", string="Employees")

    def compute_sheet(self):
        summary_lines = self.env["hr.payslip.summary.line"]
        [data] = self.read()
        active_id = self.env.context.get("active_id")
        if active_id:
            summary = self.env["hr.payslip.summary"].browse(active_id)

        if not data["employee_ids"]:
            raise UserError(_("You must select employee(s) to generate payslip summary."))
        sequence = 0
        summary.line_ids.unlink()
        for employee in self.env["hr.employee"].browse(data["employee_ids"]):
            sequence = sequence + 1
            res = {
                "sequence": sequence,
                "employee_id": employee.id,
                "summary_id": active_id,
                "date_range_id": summary.date_range_id.id,
            }
            summary_lines += self.env["hr.payslip.summary.line"].create(res)
        summary_lines.compute_sheet()
        return {"type": "ir.actions.act_window_close"}
