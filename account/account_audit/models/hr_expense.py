from odoo import models, api, fields


class HRExpense(models.Model):
    _inherit = "hr.expense"

    payment_mode = fields.Selection(default='company_account')
