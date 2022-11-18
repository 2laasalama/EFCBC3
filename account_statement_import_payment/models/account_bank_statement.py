# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.onchange('balance_end')
    def onchange_balance_end(self):
        self.balance_end_real = self.balance_end
