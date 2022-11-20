# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_validate_or_action(self):
        self.balance_end_real = self.balance_end
        return super(AccountBankStatement, self).button_validate_or_action()
