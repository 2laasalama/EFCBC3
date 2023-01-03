# -*- coding: utf-8 -*-
import requests
import json
import logging

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError

from ..bpm_integration import *

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_number = fields.Char(readonly=True)
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

    def action_post(self):
        for rec in self:
            rec.bpm_payment_action('confirm')
        return super(AccountPayment, self).action_post()

    def action_cancel(self):
        for rec in self:
            rec.bpm_payment_action('cancel')
        return super(AccountPayment, self).action_cancel()

    def bpm_payment_action(self, action):
        payload_body = self.format_request_data(action, "notes...", self.id, self.name, self.payment_number)
        route = "/bonita/API/bpm/message"
        request_type = 'post'
        name = '{} - {}'.format(action, self.name)
        self.env['bpm.request'].add_bpm_request(self, name, route, request_type, payload_body)

    def format_request_data(self, status, notes, payment_id, paymentSerialNumber, requestPaymentNumber):
        vals = {
            "messageName": "firstPaymentRequest",
            "targetProcess": "دورة عمل تسجيل مقاول لأول مرة",
            "messageContent": {
                "paymentOrderNumber": {
                    "value": str(payment_id)
                },
                "paymentSerialNumber": {
                    "value": paymentSerialNumber
                },
                "notes": {
                    "value": notes
                },
                "receiptImage": {
                    "value": "receiptImage"
                },
                "status": {
                    "value": status
                }
            },
            "correlations": {
                "requestPaymentNumber": {
                    "value": requestPaymentNumber
                }
            }
        }
        return vals
