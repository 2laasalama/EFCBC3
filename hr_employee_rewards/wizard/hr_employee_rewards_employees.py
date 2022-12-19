from odoo import _, fields, models
from odoo.exceptions import UserError


class HrRewardsEmployees(models.TransientModel):
    _name = "hr.employee.rewards.employees"

    employee_ids = fields.Many2many("hr.employee", string="Employees")

    def compute_sheet(self):
        [data] = self.read()
        active_id = self.env.context.get("active_id")
        if active_id:
            active_record = self.env["hr.employee.rewards"].browse(active_id)

        if not data["employee_ids"]:
            raise UserError(_("You must select employee(s)."))

        active_record.line_ids.unlink()

        for employee in self.env["hr.employee"].browse(data["employee_ids"]):
            res = {
                "employee_id": employee.id,
                "rewards_id": active_id,
                "date_range_id": active_record.date_range_id.id,
            }
            self.env["hr.employee.rewards.line"].create(res)
        return {"type": "ir.actions.act_window_close"}
