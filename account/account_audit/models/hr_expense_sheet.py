from odoo import models, api, fields


class ExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    payment_id = fields.Many2one('account.payment', string='Payment')
