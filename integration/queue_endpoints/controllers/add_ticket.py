import functools
import logging
import datetime

try:
    import simplejson as json
except ImportError:
    import json
from odoo import http, _
from odoo.http import request
from odoo import fields
from odoo.addons.rest_api.rest_exception import invalid_response, valid_response, invalid_token
from odoo.addons.rest_api.controllers.main import check_valid_token
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


def valid_request_data(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        request_data = json.loads(request.httprequest.data)

        mandatory_data = [('date', 'str'), ('department_id', 'int'), ('department_name', 'str'),
                          ('name', 'str'), ('phone', 'str')]

        optional_data = []

        all_data = mandatory_data + optional_data

        mandatory_fields = list(zip(*mandatory_data))[0]

        all_fields = mandatory_fields

        missing = [item for item in mandatory_fields if item not in request_data.keys()]
        unknown = [item for item in request_data.keys() if item not in all_fields]

        if unknown:
            info = "Three is unknown fields {}".format(unknown)
            return invalid_response(400, 'unknownError', info)

        if missing:
            info = "you missing required fields {}".format(missing)
            return invalid_response(400, 'MissingError', info)

        for item in all_data:
            if item[0] in request_data and not type(request_data[item[0]]) is eval(item[1]):
                info = ("{} field Must be in type {}").format(item[0], item[1])
                return invalid_response(400, 'ValidationError', info)
        try:
            datetime.datetime.strptime(request_data['date'], '%Y-%m-%d')
        except ValueError:
            info = "Incorrect date format, should be YYYY-MM-DD"
            return invalid_response(400, 'ValidationError', info)

        return func(self, *args, **kwargs)

    return wrap


class ControllerREST(http.Controller):

    @http.route('/api/add/ticket', methods=['POST'], type='json', auth='none', csrf=False)
    @check_valid_token
    @valid_request_data
    def add_ticket(self, **kw):
        request_data = json.loads(request.httprequest.data)
        department_id = int(request_data['department_id'])
        department = request.env['department.department'].sudo().search([('ref', '=', department_id)])
        if not department:
            department = request.env['department.department'].sudo().create({
                'name': request_data['department_id'],
                'ref': department_id
            })

        vals = {
            'token_dept': department.id,
            'date': request_data['date'],
            'user_mobile': request_data['phone'],
            'name': request_data['name'],
        }

        try:
            with request.env.cr.savepoint():
                ticket = request.env['token.token'].sudo().create(vals)
                return valid_response({"number": ticket.token_ref})
        except Exception as e:
            info = ("{}").format(e)
            error = 'ValidationError'
            return invalid_response(400, error, info)
