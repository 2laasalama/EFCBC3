# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_number = fields.Integer()
    receipt_number = fields.Char()
    cancel_reason = fields.Char()
    request_type = fields.Char()

    @api.constrains('payment_number')
    def _check_payment_number_constraint(self):
        """ rec payment_number must be unique """
        for rec in self.filtered(lambda p: p.payment_number):
            domain = [('id', '!=', rec.id), ('payment_number', '=', rec.payment_number)]
            if self.search(domain):
                raise ValidationError(_('payment number must be unique!'))
