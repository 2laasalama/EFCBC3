from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_payment_order = fields.Boolean()
    type = fields.Selection([('cash', 'Cash'), ('check', 'Check')], default='cash')
    payment_order_num = fields.Char(string='Payment Order #', readonly=True)
    payment_permission_num = fields.Char(string='Payment Permission #', readonly=True)
    payment_order_state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancel'), ('posted', 'Posted')], default='draft')

    def action_confirm(self):
        for rec in self:
            if rec.has_expense:
                expense_id = self.env['hr.expense.sheet'].search([('payment_id', '=', self.id)])
                if not expense_id:
                    raise ValidationError(_('You must add expenses to be posted'))
                expense_id.approve_expense_sheets()
                expense_id.action_sheet_move_create()
            else:
                rec.action_post()

            rec.payment_order_state = 'posted'

    def button_open_journal_entry(self):
        self.ensure_one()
        if self.has_expense:
            expense_id = self.env['hr.expense.sheet'].search([('payment_id', '=', self.id)])
            return {
                'name': expense_id.account_move_id.name,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': expense_id.account_move_id.id
            }
        else:
            super().button_open_journal_entry()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountPayment, self).create(vals_list)
        if res.company_id.payment_order_sequence:
            res.payment_order_num = res.company_id.payment_order_sequence.next_by_id()
        if res.company_id.payment_permission_sequence:
            res.payment_permission_num = res.company_id.payment_permission_sequence.next_by_id()
        return res
