from odoo import models, api, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_expense_treasury = fields.Boolean()
