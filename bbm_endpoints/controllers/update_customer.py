import functools
import logging

try:
    import simplejson as json
except ImportError:
    import json
from odoo import http, _
from odoo.http import request
from odoo.addons.rest_api.rest_exception import invalid_response, valid_response, check_data_validation
from odoo.addons.rest_api.controllers.main import check_valid_token

_logger = logging.getLogger(__name__)


def valid_request_data(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        request_data = json.loads(request.httprequest.data)

        mandatory_data = []

        optional_data = [('name', 'str'), ('uuid', 'str'), ('mobile', 'str'), ('email', 'str'), ('id_number', 'str'),
                         ('address', 'str'), ('identification_type', 'str'), ('company_type', 'str'),
                         ('bank_account', 'str'), ('nationality_code', 'str')]

        error, info = check_data_validation(request_data, mandatory_data, optional_data)

        if error:
            return invalid_response(400, error, info)

        if 'company_type' in request_data:
            if request_data['company_type'] not in ['person', 'company']:
                info = "company_type must be person or company"
                error = 'ValidationError'
                return invalid_response(400, error, info)

        if 'uuid' in request_data:
            if request.env['res.partner'].sudo().search([('uuid', '=', request_data['uuid'])]):
                info = "Customer already exists! uuid must be unique"
                error = 'invalid_data'
                return invalid_response(400, error, info)

        return func(self, *args, **kwargs)

    return wrap


class ControllerREST(http.Controller):

    @http.route('/api/update/customer/<string:customer_id>', methods=['POST'], type='json', auth='none', csrf=False)
    @check_valid_token
    @valid_request_data
    def update_customer(self, customer_id, **kw):
        request_data = json.loads(request.httprequest.data)
        partner = request.env['res.partner'].sudo().search([('id', '=', int(customer_id))])
        if not partner:
            info = "customer id is not exists in database!"
            error = 'invalid_data'
            return invalid_response(400, error, info)

        if 'uuid' in request_data and request.env['res.partner'].sudo().search([('uuid', '=', request_data['uuid'])]):
            info = "Customer uuid already exists! uuid must be unique"
            error = 'invalid_data'
            return invalid_response(400, error, info)

        country = False
        if 'nationality_code' in request_data:
            country = request.env['res.country'].sudo().search(
                [('currency_id.name', '=', request_data['nationality_code'])])
            if not country:
                info = "Nationality Code is not exists in database!"
                error = 'invalid_data'
                return invalid_response(400, error, info)

        vals = self.reformat_data(request_data)
        vals['country_id'] = country.id if country else False
        try:
            with request.env.cr.savepoint():
                partner.sudo().update(vals)
                return valid_response({"contractorID": partner.id})
        except Exception as e:
            info = ("{}").format(e)
            error = 'ValidationError'
            return invalid_response(400, error, info)

    def reformat_data(self, request_data):

        vals = {
            'name': request_data.get('name', False),
            'uuid': request_data.get('uuid', False),
            'mobile': request_data.get('mobile', False),
            'email': request_data.get('email', False),
            'id_number': request_data.get('id_number', False),
            'street': request_data.get('address', False),
            'company_type': request_data.get('company_type', False),
            'identification_type': request_data.get('identification_type', False),
            'bank_ids': [
                (0, 0, {'acc_number': request_data.get(
                    'bank_account')})] if 'bank_account' in request_data else False,
        }
        vals = {key: val for key, val in vals.items() if val != False}

        return vals
