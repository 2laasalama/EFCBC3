# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportStockRule(models.AbstractModel):
    _name = 'report.account_treasury.draft_payment_template'
    _description = 'Stock rule report'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [('type', '=', data['type']),
                  ('date', '=', data['date']),
                  ('payment_order_state', '=', 'draft'),
                  ('is_payment_order', '=', True)]
        journal = self.env['account.journal'].browse(data['journal_id'])
        if journal:
            domain.append(('journal_id', '=', journal.id))

        payments = self.env['account.payment'].search(domain)
        # all_journal

        data['journal_name'] = journal.name if not data['all_journal'] else 'الكل'

        return {
            'doc_ids': payments.ids if payments else False,
            'doc_model': 'account.payment',
            'data': data,
            'docs': payments,
        }
