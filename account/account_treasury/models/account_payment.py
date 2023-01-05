from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def get_treasury_journal_id(self):
        journal_id = self.env['account.journal'].search([('is_expense_treasury', '=', True)], limit=1)
        return journal_id.id if journal_id else False

    @api.model
    def _get_default_journal(self):
        if self._context.get('default_is_treasury_promotion'):
            return self.get_treasury_journal_id()
        return super()._get_default_journal()

    is_treasury_promotion = fields.Boolean()
    journal_id = fields.Many2one('account.journal', default=_get_default_journal)
    treasury_code = fields.Char(related='journal_id.code')


