import logging
import werkzeug.wrappers

try:
    import simplejson as json
except ImportError:
    import json

_logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("utf-8")
        return json.JSONEncoder.default(self, obj)


def check_data_validation(request_data, mandatory_data, optional_data):
    all_data = mandatory_data + optional_data

    mandatory_fields = list(zip(*mandatory_data))[0] if mandatory_data else ()

    optional_data = list(zip(*optional_data))[0] if optional_data else ()

    all_fields = mandatory_fields + optional_data

    missing = [item for item in mandatory_fields if item not in request_data.keys()]
    unknown = [item for item in request_data.keys() if item not in all_fields]

    if unknown:
        info = "Three is unknown fields {}".format(unknown)
        error = 'unknownError'
        return error, info

    if missing:
        info = "you missing required fields {}".format(missing)
        error = 'MissingError'
        return error, info

    for item in all_data:
        if item[0] in request_data and not type(request_data[item[0]]) is eval(item[1]):
            info = ("{} field Must be in type {}").format(item[0], item[1])
            error = 'ValidationError'
            return error, info

    return False, False


def valid_response(data):
    data.update({'rest_api_code': 200,
                 'isSuccess': True})
    return data


def invalid_response(status, error_code, error_info):
    return {
        'errorCode': error_code,
        'errorDescription': error_info,
        'rest_api_code': status,
        'isSuccess': False
    }


def invalid_object_id():
    _logger.error("Invalid object 'id'!")
    return invalid_response(400, 'invalid_object_id', "Invalid object 'id'!")


def invalid_token():
    _logger.error("Token is expired or invalid!")
    return invalid_response(401, 'invalid_token', "Token is expired or invalid!")


def modal_not_found(modal_name):
    _logger.error("Not found object(s) in odoo!")
    return invalid_response(404, 'object_not_found_in_odoo',
                            "Modal " + modal_name + " Not Found!")


def rest_api_unavailable(modal_name):
    _logger.error("Not found object(s) in odoo!")
    return invalid_response(404, 'object_not_found_in_odoo',
                            "Enable Rest API For " + modal_name + "!")


def object_not_found_all(modal_name):
    _logger.error("Not found object(s) in odoo!")
    return invalid_response(404, 'object_not_found_in_odoo',
                            "No Record found in " + modal_name + "!")


def object_not_found(record_id, modal_name):
    _logger.error("Not found object(s) in odoo!")
    return invalid_response(404, 'object_not_found_in_odoo',
                            "Record " + str(record_id) + " Not found in " + modal_name + "!")


def unable_delete():
    _logger.error("Access Denied!")
    return invalid_response(403, "you don't have access to delete records for "
                                 "this model", "Access Denied!")


def no_object_created(odoo_error):
    _logger.error("Not created object in odoo! ERROR: %s" % odoo_error)
    return invalid_response(500, 'not_created_object_in_odoo',
                            "Not created object in odoo! ERROR: %s" %
                            odoo_error)


def no_object_updated(odoo_error):
    _logger.error("Not updated object in odoo! ERROR: %s" % odoo_error)
    return invalid_response(500, 'not_updated_object_in_odoo',
                            "Object Not Updated! ERROR: %s" %
                            odoo_error)


def no_object_deleted(odoo_error):
    _logger.error("Not deleted object in odoo! ERROR: %s" % odoo_error)
    return invalid_response(500, 'not_deleted_object_in_odoo',
                            "Not deleted object in odoo! ERROR: %s" %
                            odoo_error)
