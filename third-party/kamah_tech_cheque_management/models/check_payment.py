# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions,_
from datetime import date, datetime, time, timedelta
import odoo.addons.decimal_precision as dp


class normal_payments(models.Model):
    _name = 'normal.payments'
    _rec_name = 'name'
    _description = 'Payments'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def get_user(self):
        return self._uid

    def get_currency(self):
        return self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id.id

    payment_No = fields.Char()
    name = fields.Char(string="", required=False, compute="get_title", readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner Name", required=True)
    payment_date = fields.Datetime(string="Payment Date", required=True, default=datetime.today())
    amount = fields.Float(string="Amount",compute="change_checks_ids", store=True )
    amount1 = fields.Float(string="Amount")
    guaranty_check = fields.Boolean("Guaranty Check",default=False)
    payment_method = fields.Many2one(comodel_name="account.journal", string="Payment Journal", required=True)
    payment_subtype = fields.Selection(related='payment_method.payment_subtype')
    user_id = fields.Many2one(comodel_name="res.users", default=get_user)
    currency_id = fields.Many2one(comodel_name="res.currency", default=get_currency)
    state = fields.Selection(selection=[('draft', 'Draft'), ('posted', 'Posted'), ], default='draft',
                             track_visibility='onchange')
    pay_check_ids = fields.One2many('native.payments.check.create', 'nom_pay_id', string=_('Checks'))
    send_rec_money = fields.Selection(string="Payment Type",selection=[('send','Send Money'),('rece','Receive Money')],default='rece')
    receipt_number = fields.Char(string="Receipt Number")
    account_id = fields.Many2one('account.account',string="Account Payable/Receivable")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    request_id = fields.Many2one('check.payment.request',string="Check Request",readonly=True)
    analytic_tag_id = fields.Many2one('account.analytic.tag',string="Analytic Tag")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)



    
    @api.constrains('amount')
    def _total_amount(self):
        if self.payment_subtype:
            if (self.amount) ==0.0 :
                raise exceptions.ValidationError('amount for checks must be more than zerO!')
        else:
            if (self.amount1) ==0.0 :
                raise exceptions.ValidationError('amount for payment must be more than zerO!')



    @api.onchange('partner_id','send_rec_money')
    def get_partner_acc(self):
        if self.send_rec_money == 'send':
            self.account_id = self.partner_id.property_account_payable_id.id
        elif self.send_rec_money == 'rece':
            self.account_id = self.partner_id.property_account_receivable_id.id

    
    @api.depends('pay_check_ids')
    def change_checks_ids(self):
        for rec in self:
            tot_amnt = 0.0
            if rec.sudo().payment_subtype:
                if rec.sudo().pay_check_ids:
                    for x in rec.sudo().pay_check_ids:
                        tot_amnt += x.amount
            rec.amount = tot_amnt

    
    def button_journal_entries(self):
        return {
            'name': ('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('jebal_con_pay_id', 'in', self.ids)],
        }


    @api.depends('partner_id')
    def get_title(self):
        for rec in self:
            if rec.partner_id:
                if rec.send_rec_money == 'send':
                    rec.name = "Payment for " + str(rec.partner_id.name)
                else:
                    rec.name = "Payment Receive from " + str(rec.partner_id.name)
            else:
                rec.name = '*'
            return True

    
    def action_confirm(self):
        pay_amt = 0
        if self.payment_subtype:
            pay_amt = self.amount
        else:
            pay_amt = self.amount1
        move = {

            'journal_id': self.payment_method.id,
            'ref': self.receipt_number,
            'company_id': self.user_id.company_id.id,
        }
        move_line = {

            'partner_id': self.partner_id.id,
            'ref': self.receipt_number,
            'jebal_con_pay_id': self.id,
        }
        if self.send_rec_money == 'send':
            debit_account = [{'account': self.account_id.id, 'percentage': 100 , 'analytic_id' : self.analytic_id.id, 'analytic_tag_id' : self.analytic_tag_id.id,}]
            credit_account = [{'account': self.payment_method.default_account_id.id, 'percentage': 100 }]
        else:
            credit_account = [{'account': self.account_id.id, 'percentage': 100 ,'analytic_id' : self.analytic_id.id,'analytic_tag_id' : self.analytic_tag_id.id,}]
            debit_account = [{'account': self.payment_method.default_account_id.id, 'percentage': 100}]
        amount ,credit_ml,debit_ml = self.env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                   debit_account=debit_account,
                                                   credit_account=credit_account,
                                                   src_currency=self.currency_id,
                                                   amount=pay_amt)

        self.state = 'posted'
        if self.payment_subtype:
            total = 0.0
            for check in self.pay_check_ids:
                total += check.amount

                company_currency = self.env.user.company_id.currency_id
                company = self.env.user.company_id
                debit = check.amount
                if self.currency_id != company_currency:
                    debit = self.currency_id._convert(check.amount, company_currency, company, date=datetime.today())

                check_number = check.check_number
                if self.send_rec_money == 'send':
                    if  check.book_id:
                        check_number = check.book_id.get_next_check()
                        check.check_number = check_number
                    else:
                        raise exceptions.ValidationError(_("Please Select Check Book To confirm Check Payment"))
                check_line_val = {}
                check_line_val['check_number'] = check_number
                check_line_val['check_date'] = check.check_date
                check_line_val['check_bank'] = check.bank.id
                check_line_val['dep_bank'] = check.dep_bank.id
                check_line_val['book_id'] = check.book_id.id
                check_line_val['currency_id'] = self.currency_id.id,
                if self.send_rec_money == 'rece':
                    check_line_val['state'] = 'holding'
                    check_line_val['check_type'] = 'rece'
                else:
                    check_line_val['state'] = 'handed'
                    check_line_val['check_type'] = 'pay'
                check_line_val['amount'] = check.amount
                check_line_val['open_amount'] = check.amount
                check_line_val['type'] = 'regular'
                check_line_val['amount_comp_currency'] = debit
                check_line_val['guaranty_check'] = self.guaranty_check
                check_line_val['nom_pay_id'] = self.id
                check_line_val['notespayable_id'] = self.payment_method.default_account_id.id
                check_line_val['notes_rece_id'] = self.payment_method.default_account_id.id
                check_line_val['investor_id'] = self.partner_id.id
                self.env['check.management'].create(check_line_val)

            if self.request_id:

                if total > self.request_id.amount:
                    raise exceptions.ValidationError(_("Payment Cannot exceed approved request Amount"))
                elif self.currency_id != self.request_id.currency_id:
                    raise exceptions.ValidationError(_("You Cannot change Approved Request currency"))
        return True




class payments_check_create(models.Model):

    _name = 'native.payments.check.create'
    _order = 'check_number asc'

    check_number = fields.Char(string=_("Check number"))
    check_date = fields.Date(string=_('Check Date'),required=True)
    amount = fields.Float(string=_('Amount'),required=True)
    bank = fields.Many2one('res.bank',string=_("Check Bank Name"))
    dep_bank = fields.Many2one('res.bank',string=_("Deposit Bank"))
    nom_pay_id = fields.Many2one('normal.payments')
    book_id = fields.Many2one('check.book', "Check Book" )


class CheckPaymentsRequest(models.Model):

    _name = 'check.payment.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Check Payment Request"


    def get_currency(self):
        return self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id.id

    name = fields.Char(string=_("Request"),default="New Request")
    amount = fields.Float(string=_('Amount'),required=True)
    check_date = fields.Date(string=_('Check Date'), required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", default=get_currency)
    partner_id = fields.Many2one('res.partner', string=_("Partner"),required=True)
    state = fields.Selection(selection=[('draft', 'Draft'),('submit', 'Submit'), ('validate', 'Validated'),
                                        ('approve', 'Approved')], default="draft" ,track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name']=self.env['ir.sequence'].next_by_code('check.request')
        res = super(CheckPaymentsRequest, self).create(vals)
        return res

    def submit_action(self):
        self.state = 'submit'

    def validate_action(self):
        self.state = 'validate'

    def approve_action(self):
        self.state = 'approve'
        journal=self.env['account.journal'].search([('payment_subtype','=','check')],limit=1)
        if not journal:
            raise exceptions.ValidationError(_("NO journal found for Check Please create one before approving request"))
        payment_check_vals = {}
        payment_vals = {}
        payment_check_vals['amount'] = self.amount
        payment_check_vals['check_date'] = self.check_date
        payc= self.env['native.payments.check.create'].create(payment_check_vals)
        payment_vals['account_id'] = self.partner_id.property_account_payable_id.id
        payment_vals['send_rec_money'] = 'send'
        payment_vals['partner_id'] = self.partner_id.id
        payment_vals['request_id'] = self.id
        payment_vals['payment_method'] = journal.id
        payment_vals['currency_id'] = self.currency_id.id
        payment_vals['receipt_number'] = "New Check"
        pay = self.env['normal.payments'].create(payment_vals)
        payc.nom_pay_id = pay.id