import functools
import hashlib
import os
import logging

try:
    import simplejson as json
except ImportError:
    import json
import odoo
from odoo import http, _
from odoo.http import request
from ..rest_exception import *

_logger = logging.getLogger(__name__)


def check_valid_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get('Authorization')
        if not access_token:
            info = "Missing access token in request header!"
            error = 'access_token_not_found'
            _logger.error(info)
            return invalid_response(400, error, info)

        access_token_data = request.env['oauth.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        access_token_obj = access_token_data._get_access_token(user_id=access_token_data.user_id.id)

        if not access_token_obj or access_token_obj.token != access_token:
            return invalid_token()

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


def generate_token(length=40):
    random_data = os.urandom(100)
    hash_gen = hashlib.new('sha512')
    hash_gen.update(random_data)
    return hash_gen.hexdigest()[:length]


# Read OAuth2 constants and setup token store:
db_name = odoo.tools.config.get('db_name')
if not db_name:
    _logger.warning("Warning: To proper setup OAuth - it's necessary to "
                    "set the parameter 'db_name' in odoo config file!")


# List of REST resources in current file:
#   (url prefix)            (method)     (action)
# /api/auth/get_tokens        POST    - Login in odoo and get access tokens
# /api/auth/delete_tokens     POST    - Delete access tokens from token store


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # # Login in odoo database and get access tokens:
    # @http.route('/api/add/customer', methods=['POST'], type='json',
    #             auth='none', csrf=False)
    # @check_valid_token
    # def add_customer(self, **kw):
    #     # Convert http data into json:
    #     request_data = json.loads(request.httprequest.data)
    #     if 'uuid' not in request_data or 'name' not in request_data:
    #         info = "Empty value of 'uuid' or 'name' "
    #         error = 'invalid_data'
    #         _logger.error(info)
    #         return invalid_response(400, error, info)
    #
    #     request.env['res.partner'].create({'name': request_data['name']})
    #
    #     return valid_response(
    #         {"desc": 'Customer Added Successfully'}
    #     )

    # Login in odoo database and get access tokens:
    @http.route('/api/auth/get_tokens', methods=['POST'], type='json',
                auth='none', csrf=False)
    def api_auth_gettokens(self, **kw):
        # Convert http data into json:
        request_data = json.loads(request.httprequest.data)
        db = request_data['db'] if request_data.get('db') else None
        username = request_data['username'] if request_data.get('username') else None
        password = request_data['password'] if request_data.get('password') else None
        # Compare dbname (from HTTP-request vs. odoo config):
        print(">>>>>>>",db_name)
        # if db and (db != db_name):
        #     info = "Wrong 'dbname'!"
        #     error = 'wrong_dbname'
        #     _logger.error(info)
        #     return invalid_response(400, error, info)

        # Empty 'db' or 'username' or 'password:
        if not db or not username or not password:
            info = "Empty value of 'db' or 'username' or 'password'!"
            error = 'empty_db_or_username_or_password'
            _logger.error(info)
            return invalid_response(400, error, info)
        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except:
            # Invalid database:
            info = "Invalid database!"
            error = 'invalid_database'
            _logger.error(info)
            return invalid_response(400, error, info)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "odoo User authentication failed!"
            error = 'odoo_user_authentication_failed'
            _logger.error(info)
            return invalid_response(401, error, info)

        # Generate tokens
        access_token = request.env['oauth.access_token'].sudo()._get_access_token(user_id=uid, create=True)

        # Save all tokens in store
        _logger.info("Save OAuth2 tokens of user in store...")

        return valid_response(data={
            'uid': uid,
            'access_token': access_token.token,
            'expires_in': access_token.expires,
        })

    # Delete access tokens from token store:
    @http.route('/api/auth/delete_tokens', methods=['POST'], type='http',
                auth='none', csrf=False)
    def api_auth_deletetokens(self, **post):
        # Try convert http data into json:
        access_token = request.httprequest.headers.get('access_token')
        access_token_data = request.env['oauth.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if not access_token_data:
            info = "No access token was provided in request!"
            error = 'no_access_token'
            _logger.error(info)
            return invalid_response(400, error, info)
        access_token_data.sudo().unlink()
        # Successful response:
        return valid_response(
            {"desc": 'Token Successfully Deleted', "delete": True}
        )
