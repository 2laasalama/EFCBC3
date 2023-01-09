from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_treasury_journal_id(self):
        journal_id = self.env['account.journal'].search([('is_expense_treasury', '=', True)], limit=1)
        return journal_id.id if journal_id else False

    @api.model
    def _search_default_journal(self, journal_types):
        if self._context.get('default_is_treasury_promotion'):
            return self.get_treasury_journal_id()
        return super()._search_default_journal(journal_types)
