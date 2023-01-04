  # -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import math
from odoo import models
import time
from odoo import api, fields, models, _
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError, Warning
		
class AccountBankStatement(models.Model):
	_inherit = "account.bank.statement"
	
	move_line_ids = fields.One2many('account.move.line', 'statement_id', string='Entry lines')
	account_id = fields.Many2one('account.account', related='journal_id.company_id.account_journal_payment_credit_account_id', type='many2one', string='Account', readonly=True, help='used in statement reconciliation domain, but shouldn\'t be used elswhere.')
	statement_entries_ids = fields.Many2many('account.move.line', string=' Statement Entries')

	@api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real','statement_entries_ids')
	def _end_balance(self):
		res_users_obj = self.env['res.users']
		company_currency_id = self.env.user.company_id.currency_id
		for statement in self:
			if statement.statement_entries_ids:
				statement_balance_start = statement.balance_start
				for line in statement.statement_entries_ids:
					if line.debit > 0:
						if line.account_id.id == \
								statement.journal_id.company_id.account_journal_payment_credit_account_id.id:
							statement_balance_start += line.amount_currency or line.debit
					else:
						if line.account_id.id == \
								statement.journal_id.company_id.account_journal_payment_credit_account_id.id:
							statement_balance_start += line.amount_currency or (-line.credit)
				statement.total_entry_encoding = statement_balance_start
				statement.balance_end = statement.balance_start + statement.total_entry_encoding
				statement.update({
					'difference' : statement.balance_end_real - statement.balance_end,
					})
			else:
				super(AccountBankStatement, self)._end_balance()
		
	@api.model
	def create(self, vals):
		# Dont allow adding transaction and Journal Entries in same statement.
		if vals.get('statement_entries_ids') and vals.get('line_ids'):
			se = vals.get('statement_entries_ids')[0][2]
			li = vals.get('line_ids')[0][2]
			if se != [] and li:
				raise UserError('You can Either add Journal Entries or Transactions..!')
		return super(AccountBankStatement, self).create(vals)
		
	def write(self, vals):
		# Dont allow adding transaction or Journal Entries when other is added in same statement.
		for statement in self:
			if vals.get('statement_entries_ids') or vals.get('line_ids'):
				se = []
				lis = []
				if vals.get('statement_entries_ids') and  vals.get('line_ids'):
					se = vals.get('statement_entries_ids')[0][2]
					li = vals.get('line_ids')[0][2]

				elif vals.get('statement_entries_ids') : 
					se = vals.get('statement_entries_ids')[0][2]
					li = statement.line_ids.ids
				else:
					if vals.get('line_ids'):
						se = statement.statement_entries_ids.ids
						li = vals.get('line_ids')[0][2]

				if se and li:
					raise UserError('You can Either add Journal Entries or Transactions..!')
		return super(AccountBankStatement, self).write(vals)
		
		
