from odoo import _, api, fields, models


class AccountTreasuryReportWizard(models.TransientModel):
    _name = "account.treasury.report.wizard"
    _description = "Account Treasury Report Wizard"

    payment_state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')])
    journal_id = fields.Many2one('account.journal')
    type = fields.Selection([('cash', 'Cash'), ('check', 'Check')], default='cash', required=True)
    all_journal = fields.Boolean()
    date = fields.Date(default=lambda self: fields.Date.today(), required=True)

    def print_report(self):
        data = {'type': self.type,
                'date': self.date,
                'journal_id': self.journal_id.id,
                'all_journal': self.all_journal,
                }
        return self.env.ref('account_treasury.draft_payment_permission_report').report_action(None, data=data)
