import functools
import logging

try:
    import simplejson as json
except ImportError:
    import json
from odoo import http, _
from odoo.http import request
from odoo.addons.rest_api.rest_exception import invalid_response, valid_response
from odoo.addons.rest_api.controllers.main import check_valid_token

_logger = logging.getLogger(__name__)


def valid_request_data(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        request_data = json.loads(request.httprequest.data)

        mandatory_data = [('name', 'str'), ('uuid', 'str')]

        optional_data = [('mobile', 'str'), ('email', 'str'), ('id_number', 'str'),
                         ('address', 'str'),
                         ('company_type', 'str'), ('bank_account', 'str')]

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

        if 'company_type' in request_data:
            if request_data['company_type'] not in ['person', 'company']:
                info = "company_type must be person or company"
                error = 'ValidationError'
                return invalid_response(400, error, info)

        return func(self, *args, **kwargs)

    return wrap


class ControllerREST(http.Controller):

    @http.route('/api/add/customer', methods=['POST'], type='json', auth='none', csrf=False)
    @check_valid_token
    @valid_request_data
    def add_customer(self, **kw):
        request_data = json.loads(request.httprequest.data)
        if request.env['res.partner'].sudo().search([('uuid', '=', request_data['uuid'])]):
            info = "Customer already exists! uuid must be unique"
            error = 'invalid_data'
            return invalid_response(400, error, info)

        vals = {
            'customer_rank': 1,
            'name': request_data['name'],
            'uuid': request_data['uuid'],
            'mobile': request_data.get('mobile') or False,
            'email': request_data.get('email') or False,
            'id_number': request_data.get('id_number') or False,
            'street': request_data.get('address') or False,
            'company_type': request_data.get('company_type') or False,
            'bank_ids': [
                (0, 0, {'acc_number': request_data.get(
                    'bank_account')})] if 'bank_account' in request_data else False,
        }

        try:
            with request.env.cr.savepoint():
                partner = request.env['res.partner'].sudo().create(vals)
                return valid_response({"contractorID": partner.id})
        except Exception as e:
            info = ("{}").format(e)
            error = 'ValidationError'
            return invalid_response(400, error, info)
