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
        bpm_url = self.env['ir.config_parameter'].sudo().get_param('bpm_url')
        url = "{}/bonita/API/bpm/message".format(bpm_url)
        payload_body = self.format_request_data(action, "notes...")
        payload = json.dumps(payload_body)
        access = get_bpm_access(bpm_url)
        if access:
            headers = {
                'X-Bonita-API-Token': access['token'],
                'Content-Type': 'application/json',
                'Cookie': access['cookies']
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 204:
                _logger.debug("Update Payment successfully.")
            else:
                _logger.warning("Access Fail to BPM Server.")

    def format_request_data(self, status, notes):
        vals = {
            "messageName": "firstPaymentRequest",
            "targetProcess": "دورة عمل تسجيل مقاول لأول مرة",
            "messageContent": {
                "paymentOrderNumber": {
                    "value": "123456"
                },
                "paymentSerialNumber": {
                    "value": "12345678"
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
                    "value": "12345678"
                }
            }
        }
        return vals
