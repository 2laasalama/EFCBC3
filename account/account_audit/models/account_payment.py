from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_payment_order = fields.Boolean()
    has_expense = fields.Boolean()
    expense_id = fields.Many2one('hr.expense.sheet', string='Expense')

    def open_expense_sheet(self):
        res_id = self.env['hr.expense.sheet'].search([('payment_id', '=', self.id)])
        self.expense_id = res_id.id
        return {
            'name': _("Expenses"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "context": {"create": False, "default_payment_id": self.id},
            'target': 'current',
            'res_model': 'hr.expense.sheet',
            'res_id': res_id.id if res_id else False,
            'view_id': self.env.ref('account_audit.view_hr_expense_sheet_form').id,
        }


