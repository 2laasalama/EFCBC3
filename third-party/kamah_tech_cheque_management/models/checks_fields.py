# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions,_
import odoo.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
from odoo.fields import Date as fDate

class check_management(models.Model):

    _name = 'check.management'
    _description = 'Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    check_number = fields.Char(string=_("Check Number"),default="0")
    book_id = fields.Many2one('check.book', "Check Book")
    check_date = fields.Date(string=_("Check Date"),required=True)
    check_bank = fields.Many2one('res.bank', string=_('Check Bank'))
    dep_bank = fields.Many2one('res.bank', string=_('Deposit Bank'))
    check_note = fields.Char(string=_("Check Note"))
    amount = fields.Float(string=_('Check Amount'),digits=dp.get_precision('Product Price'))
    amount_app = fields.Float(string=_('Check Amount Approved'),digits=dp.get_precision('Product Price'))
    amount_reg = fields.Float(string="Check Regular Amount", digits=dp.get_precision('Product Price'))
    open_amount_reg = fields.Float(string="Check Regular Open Amount", digits=dp.get_precision('Product Price'))
    open_amount = fields.Float(string=_('Open Amount'), digits=dp.get_precision('Product Price'),track_visibility='onchange')
    amount_comp_currency = fields.Float(string="Amount Comp Currency")
    guaranty_check = fields.Boolean("Guaranty Check", default=False)
    nom_pay_id = fields.Many2one('normal.payments',"Payment")
    investor_id = fields.Many2one('res.partner',string=_("Partner"))
    type = fields.Selection(string="Type", selection=[('reservation', 'Reservation Installment'),
                                                      ('contracting', 'Contracting Installment'),
                                                      ('regular', 'Regular Installment'),
                                                      ('ser', 'Services Installment'),
                                                      ('garage', 'Garage Installment'),
                                                      ('mod', 'Modification Installment'),
                                                      ], required=True,translate=True,
                            default="regular")
    state = fields.Selection(selection=[('holding','Holding'),('deposited','Deposited'),
                                         ('approved','Approved'),('rejected','Rejected')
                                         , ('returned', 'Returned'), ('handed', 'Handed'),
                                        ('debited', 'Debited'),('canceled', 'Canceled'),('cs_return','Customer Returned')]
                             ,translate=True,track_visibility='onchange')
    currency_id = fields.Many2one('res.currency')
    notes_rece_id = fields.Many2one('account.account')
    under_collect_id  = fields.Many2one('account.account')
    notespayable_id = fields.Many2one('account.account')
    under_collect_jour = fields.Many2one('account.journal')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    check_type = fields.Selection(selection=[('rece','Notes Receivable'),('pay','Notes Payable')])
    check_state = fields.Selection(selection=[('active','Active'),('suspended','Suspended')],default='active')
    check_from_check_man = fields.Boolean(string="Check Management",default=False)
    will_collection_user = fields.Date(string="Bank Maturity Date"  ,track_visibility='onchange')





    @api.model
    def create(self,vals):
        if 'amount' in vals:
            vals['open_amount'] = vals['amount']
        return super(check_management,self).create(vals)


    def write(self, vals):
        for rec in self:
            if 'amount' in vals:
                rec.open_amount = vals['amount']
        return super(check_management, self).write(vals)


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,submenu=False):
        res = super(check_management, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)
        if 'fields' in res:
            if 'state' in res['fields']:
                if 'menu_sent' in self.env.context:
                    if self.env.context['menu_sent'] in ('handed','debited','pay'):
                        res['fields']['state']['selection'] = [('handed', 'Handed'), ('debited', 'Debited'),('canceled', 'Canceled')]
                        if self.env.context['lang'] == 'ar_SY':
                            res['fields']['state']['selection'] = [('handed', 'مسلمة'), ('debited', 'محصلة'),('canceled', 'ملغله')]
                    else:
                        res['fields']['state']['selection'] = [('holding', 'Holding'), ('deposited', 'Deposited'), ('approved', 'Approved'),
                                                               ('rejected', 'Rejected'), ('returned', 'Returned'),('canceled', 'Canceled')
                                                               ,('cs_return','Customer Returned')]
                        if self.env.context['lang'] == 'ar_SY':
                            res['fields']['state']['selection'] = [('holding', 'قابضة'), ('deposited', 'مودعة'),
                                                                   ('approved', 'خالصة'),('rejected', 'مرفوضة'), ('returned', 'مرتجعة'),
                                                                   ('canceled', 'ملغله'),('cs_return','مرتجع للعميل')]
        if 'toolbar' in res:
            if 'menu_sent' in self.env.context:
                if self.env.context['menu_sent'] == 'holding':
                    for i in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][i]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][i]
                            break
                    for i in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][i]['name'] == 'Company Return':
                            del res['toolbar']['action'][i]
                            break
                    for i in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][i]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][i]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'deposit':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'approved':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'rejected':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'returned':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'handed':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'pay':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'debited':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'canceled':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
                if self.env.context['menu_sent'] == 'cs_return':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Deposit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Vendor Return':
                            del res['toolbar']['action'][j]
                            break
        return res

class check_book(models.Model):

    _name = 'check.book'
    _description = 'Check Book'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Book Name" )
    no_digits = fields.Char("No Of Digits",default=0)
    start_check_no = fields.Integer("Start Check No.",required=True)
    last_check_no = fields.Integer("Last Check No.")
    next_check_no = fields.Integer("Next Check No.",readonly=True)
    bank_id = fields.Many2one('res.bank',"Bank" ,required = True)
    check_ids = fields.One2many('check.management','book_id',"Book Checks")
    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('active', 'Active'),
                                        ('closed', 'Closed')], default="draft", track_visibility='onchange')

    def active_action(self):
        self.state='active'
        self.next_check_no = self.start_check_no
        if not self.name:
            self.name = "CheckBook "+str(self.bank_id.name)

    def close_action(self):
        self.state='closed'

    def cancel_current_check_action(self):

        check_line_val = {'check_number': self.get_next_check(), 'check_date': datetime.today(),
                          'check_bank': self.bank_id.id, 'book_id': self.id,
                          'currency_id': self.env.user.company_id.currency_id.id, 'state': 'canceled',
                          'check_type': 'pay'}
        self.env['check.management'].create(check_line_val)

    def get_next_check(self):
        digit ="0"+str(self.no_digits)
        check_no= str(format(self.next_check_no,digit ))
        self.next_check_no += 1

        if self.next_check_no > self.last_check_no:
            self.next_check_no = 0
            self.state = 'closed'

        return check_no