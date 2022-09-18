from odoo.http import JsonRequest
import json
from odoo.tools import date_utils
from odoo.http import request, Response


class JsonRequestPatch(JsonRequest):

    def _json_response(self, result=None, error=None):
        response = {
            'jsonrpc': '2.0',
            'id': self.jsonrequest.get('id')
        }

        code = 200

        if error is not None:
            response['error'] = error
        if result is not None:
            response['result'] = result

        if isinstance(result, dict) and 'rest_api_code' in result:
            code = int(result['rest_api_code'])
            result.pop('rest_api_code')
            response.pop('result')
            response.update(result)

        mime = 'application/json'
        body = json.dumps(response, default=date_utils.json_default)

        return Response(
            body, status=error and error.pop('http_status', code) or code,
            headers=[('Content-Type', mime), ('Content-Length', len(body))]
        )


JsonRequest._json_response = JsonRequestPatch._json_response
