import functools
import logging

try:
    import simplejson as json
except ImportError:
    import json
from odoo import http, _
from odoo.http import request
from odoo.addons.rest_api.rest_exception import invalid_response, valid_response, invalid_token
from odoo.addons.rest_api.controllers.main import check_valid_token

_logger = logging.getLogger(__name__)


def valid_request_data(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        request_data = json.loads(request.httprequest.data)

        mandatory_data = [('payment_number', 'str'), ('date', 'str'), ('payment_type', 'str'),
                          ('amount', 'float'),
                          ('journal', 'str'), ('state', 'str')]

        optional_data = [('notes', 'str'), ('customer_id', 'int'), ('currency_code', 'str'),
                         ('bank_account', 'str'), ('receipt_number', 'str'),
                         ('request_type', 'str')]

        all_data = mandatory_data + optional_data

        mandatory_fields = list(zip(*mandatory_data))[0]

        all_fields = mandatory_fields + list(zip(*optional_data))[0]

        missing = [item for item in mandatory_fields if item not in request_data.keys()]
        unknown = [item for item in request_data.keys() if item not in all_fields]

        if unknown:
            info = "Three is unknown fields {}".format(unknown)
            error = 'unknownError'
            return invalid_response(400, error, info)

        if missing:
            info = "you missing required fields {}".format(missing)
            error = 'MissingError'
            return invalid_response(400, error, info)

        for item in all_data:
            if item[0] in request_data and not type(request_data[item[0]]) is eval(item[1]):
                info = ("{} field Must be in type {}").format(item[0], item[1])
                error = 'ValidationError'
                return invalid_response(400, error, info)

        if 'payment_type' in request_data:
            if request_data['payment_type'] not in ['inbound', 'outbound']:
                info = "Payment type must be inbound or outbound"
                error = 'ValidationError'
                return invalid_response(400, error, info)

        if 'journal' in request_data:
            if request_data['journal'] not in ['bank', 'cash']:
                info = "journal must be bank or cash"
                error = 'ValidationError'
                return invalid_response(400, error, info)

        if 'state' in request_data:
            if request_data['state'] not in ['draft', 'done']:
                info = "state must be draft or done"
                error = 'ValidationError'
                return invalid_response(400, error, info)

        return func(self, *args, **kwargs)

    return wrap


def valid_cancel_data(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        request_data = json.loads(request.httprequest.data)

        mandatory_data = [('payment_number', 'str'), ('cancel_reason', 'str')]

        optional_data = []

        all_data = mandatory_data

        mandatory_fields = list(zip(*mandatory_data))[0]

        all_fields = mandatory_fields

        missing = [item for item in mandatory_fields if item not in request_data.keys()]
        unknown = [item for item in request_data.keys() if item not in all_fields]

        if unknown:
            info = "Three is unknown fields {}".format(unknown)
            error = 'unknownError'
            return invalid_response(400, error, info)

        if missing:
            info = "you missing required fields {}".format(missing)
            error = 'MissingError'
            return invalid_response(400, error, info)

        for item in all_data:
            if item[0] in request_data and not type(request_data[item[0]]) is eval(item[1]):
                info = ("{} field Must be in type {}").format(item[0], item[1])
                error = 'ValidationError'
                return invalid_response(400, error, info)

        return func(self, *args, **kwargs)

    return wrap


class ControllerREST(http.Controller):

    @http.route('/api/add/payment', methods=['POST'], type='json', auth='none', csrf=False)
    @check_valid_token
    @valid_request_data
    def add_payment(self, **kw):
        request_data = json.loads(request.httprequest.data)

        if request.env['account.payment'].sudo().search(
                [('payment_number', '=', request_data['payment_number'])]):
            info = "Payment already exists! payment_number must be unique"
            error = 'invalid_data'
            return invalid_response(400, error, info)

        customer = False
        if 'customer_id' in request_data:
            customer = request.env['res.partner'].sudo().search(
                [('id', '=', request_data['customer_id'])])
            if not customer:
                info = "Three is no customer with uuid '{}'. Please Define it and retry.".format(
                    request_data['customer_id'])
                error = 'MissingError'
                return invalid_response(400, error, info)

        currency = False
        if 'currency_code' in request_data:
            currency = request.env['res.currency'].sudo().search(
                [('name', '=', request_data['currency_code'])])
            if not currency:
                info = "Three is no currency with code '{}'. Please Define it and retry.".format(
                    request_data['currency_code'])
                error = 'MissingError'
                return invalid_response(400, error, info)

        journal = request.env['account.journal'].sudo().search(
            [('type', '=', request_data['journal'])], limit=1)
        if not journal:
            info = "Three is no journal with type '{}'. Please Define it and retry.".format(
                request_data['journal'])
            error = 'MissingError'
            return invalid_response(400, error, info)

        if 'bank_account' in request_data and not customer:
            info = "You Can not add Bank Account Without Customer."
            error = 'MissingError'
            return invalid_response(400, error, info)

        bank_account = False
        if 'bank_account' in request_data:
            bank_account = request.env['res.partner.bank'].sudo().search(
                [('acc_number', '=', request_data['bank_account']),
                 ('partner_id', '=', customer.id)],
                limit=1)
            if not bank_account:
                bank_account = request.env['res.partner.bank'].sudo().create({
                    'acc_number': request_data['bank_account'],
                    'partner_id': customer.id
                })

        if request_data['state'] == 'done' and not 'receipt_number' in request_data:
            info = "You Can not add confirmed payment order Without receipt number.".format(
                request_data['journal'])
            error = 'MissingError'
            return invalid_response(400, error, info)

        vals = {
            'payment_number': request_data['payment_number'],
            'payment_type': request_data.get('payment_type') or False,
            'amount': request_data.get('amount') or False,
            'date': request_data.get('date') or False,
            'ref': request_data.get('notes') or False,
            'partner_id': customer.id if customer else False,
            'journal_id': journal.id if journal else False,
            'currency_id': currency.id if currency else False,
            'partner_bank_id': bank_account.id if bank_account else False,
            'receipt_number': request_data.get('receipt_number') or False,
            'request_type': request_data.get('request_type') or False,
        }

        try:
            with request.env.cr.savepoint():
                payment = request.env['account.payment'].sudo().create(vals)
                if request_data['state'] == 'done':
                    payment.sudo().action_post()
                return valid_response({"Massage": 'Payment Order Added Successfully'})
        except Exception as e:
            info = ("{}").format(e)
            error = 'ValidationError'
            return invalid_response(400, error, info)

    @http.route('/api/cancel/payment', methods=['POST'], type='json', auth='none', csrf=False)
    @check_valid_token
    @valid_cancel_data
    def cancel_payment(self, **kw):
        request_data = json.loads(request.httprequest.data)

        payment = request.env['account.payment'].sudo().search(
            [('payment_number', '=', request_data['payment_number'])])
        if not payment:
            info = "Payment doesn't exists! Three is no payment with payment number [{}]".format(
                request_data['payment_number'])
            error = 'MissingError'
            return invalid_response(400, error, info)

        try:
            with request.env.cr.savepoint():
                payment.sudo().action_cancel()
                payment.sudo().update({'cancel_reason': request_data['cancel_reason']})
                return valid_response({"Massage": 'Payment Canceled Successfully'})
        except Exception as e:
            info = ("{}").format(e)
            error = 'ValidationError'
            return invalid_response(400, error, info)
