from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta



class move_lines(models.Model):

    _inherit = 'account.move.line'

    jebal_pay_id = fields.Integer(string="Jebal Payment",index=True)
    jebal_check_id = fields.Integer(string="Jebal Check",index=True)
    jebal_nrom_pay_id = fields.Integer(string="Jebal Check", index=True)
    jebal_con_pay_id = fields.Integer(string="Jebal Check", index=True)
    date_maturity = fields.Date(string='Due date', index=True, required=False,
                                help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")

    @api.model_create_multi
    def create(self,vals):
        res = super(move_lines,self).create(vals)
        res.date_maturity = False
        return res


class create_moves(models.Model):
    _name = 'create.moves'


    def create_move_lines(self, **kwargs):
        self.accounts_agg(**kwargs)
        self.adjust_move_percentage(**kwargs)
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        company_currency = self.env.user.company_id.currency_id
        company = self.env.user.company_id
        currency = kwargs['src_currency']

        if currency and currency != company_currency:
            balance = currency._convert(kwargs['amount'], company_currency, company, date=datetime.today())
            amount_currency = kwargs['amount']
            currency_id = currency.id
        else:
            amount_currency = 0.0
            balance = kwargs['amount']
            currency_id = False
        debit = balance > 0.0 and balance or 0.0
        credit = balance < 0.0 and -balance or 0.0
        move_vals = {
            'journal_id': kwargs['move']['journal_id'],
            'date': datetime.today(),
            'ref': kwargs['move']['ref'],
            'company_id': kwargs['move']['company_id'],
        }

        move = self.env['account.move'].with_context(check_move_validity=False).create(move_vals)
        amount = debit
        if credit > 0:
            amount = credit
        for index in kwargs['debit_account']:
            debit_line_vals = {

                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': (index['percentage'] / 100) * debit,
                'credit': credit,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
            }
            if 'analytic_id' in index and index['analytic_id']:
                debit_line_vals['analytic_account_id'] = index['analytic_id']
            if 'analytic_tag_id' in index and index['analytic_tag_id']:
                debit_line_vals['analytic_tag_ids'] = [(4, index['analytic_tag_id'])]
            if 'jebal_pay_id' in kwargs['move_line']:
                debit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                debit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']
            if 'jebal_con_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_con_pay_id'] = kwargs['move_line']['jebal_con_pay_id']
            debit_line_vals['move_id'] = move.id
            debit_ml =aml_obj.create(debit_line_vals)

        for index in kwargs['credit_account']:
            credit_line_vals = {

                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': credit,
                'credit': (index['percentage'] / 100) * debit,
                'amount_currency': -1 * amount_currency,
                'currency_id': currency_id,
            }
            if 'analytic_id' in index  and index['analytic_id']:
                credit_line_vals['analytic_account_id'] = index['analytic_id']
            if 'analytic_tag_id' in index and index['analytic_tag_id']:
                credit_line_vals['analytic_tag_ids'] = [(4, index['analytic_tag_id'])]
            if 'jebal_pay_id' in kwargs['move_line']:
                credit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                credit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                credit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']
            credit_line_vals['move_id'] = move.id
            credit_ml =aml_obj.create(credit_line_vals)

        return amount ,credit_ml,debit_ml

    def adjust_move_percentage(self,**kwargs):
        # Debit
        tot_dens = 0.0
        tot_crds = 0.0
        for debs in kwargs['debit_account']:
            tot_dens+=debs['percentage']
        for crds in kwargs['credit_account']:
            tot_crds+=crds['percentage']
        percent = 100.0
        if tot_crds < 99 or tot_crds > 101:
            percent = tot_crds
        for i in range(len(kwargs['debit_account'])):
            kwargs['debit_account'][i]['percentage'] = round(kwargs['debit_account'][i]['percentage'],8)
        for index in kwargs['debit_account']:
            percent -= index['percentage']
        diff = 0.0
        if percent !=0.0:
            diff = percent / len(kwargs['debit_account'])
            for i in range(len(kwargs['debit_account'])):
                kwargs['debit_account'][i]['percentage'] +=diff
        #Credit
        percent = 100.0
        if tot_crds < 99 or tot_crds > 101:
            percent = tot_crds
        for i in range(len(kwargs['credit_account'])):
            kwargs['credit_account'][i]['percentage'] = round(kwargs['credit_account'][i]['percentage'], 8)
        for index in kwargs['credit_account']:
            percent -= index['percentage']
        diff = 0.0
        if percent != 0.0:
            diff = percent / len(kwargs['credit_account'])
            for i in range(len(kwargs['credit_account'])):
                kwargs['credit_account'][i]['percentage'] += diff

    def accounts_agg(self,**kwargs):
        all_crd_accs = {}
        for crd_accs in kwargs['credit_account']:
            if all_crd_accs and crd_accs['account'] in all_crd_accs:
                all_crd_accs[crd_accs['account']] += crd_accs['percentage']
            else:
                all_crd_accs[crd_accs['account']] = crd_accs['percentage']
        credit_account = []
        for acc_key in all_crd_accs:
            credit_account.append({'account': acc_key, 'percentage': all_crd_accs[acc_key]})
        kwargs['credit_account'] = credit_account
        all_crd_accs = {}
        for crd_accs in kwargs['debit_account']:
            if all_crd_accs and crd_accs['account'] in all_crd_accs:
                all_crd_accs[crd_accs['account']] += crd_accs['percentage']
            else:
                all_crd_accs[crd_accs['account']] = crd_accs['percentage']
        debit_account = []
        for acc_key in all_crd_accs:
            debit_account.append({'account': acc_key, 'percentage': all_crd_accs[acc_key]})
        kwargs['debit_account'] = debit_account
