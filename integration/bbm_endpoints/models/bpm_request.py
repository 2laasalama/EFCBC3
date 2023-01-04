# -*- coding: utf-8 -*-
import time
import threading

from odoo import api, fields, models, modules, _
from ..bpm_integration import *

_logger = logging.getLogger(__name__)


class BPMRequest(models.Model):
    _name = 'bpm.request'
    _order = "id desc"

    @api.model
    def add_bpm_request(self, record, name, route, type, body):
        request = self.create({'name': name,
                               'route': route,
                               'type': type,
                               'body': body,
                               'resource_ref': '%s,%s' % (record._name, record.id)})

        request.action_run()

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    def _get_default_server_url(self):
        bpm_url = self.env['ir.config_parameter'].sudo().get_param('bpm_url')
        return bpm_url

    name = fields.Char()
    server_url = fields.Char(string='Server URL', readonly=1, default=lambda self: self._get_default_server_url())
    route = fields.Char(readonly=1)
    full_url = fields.Char(string='URL')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('fail', 'Fail'), ('cancel', 'Cancel')],
                             default='draft')
    type = fields.Selection([('post', 'POST'), ('get', 'GET')], default='post', readonly=1)
    resource_ref = fields.Reference(string='Record', selection='_selection_target_model')
    body = fields.Text()
    response = fields.Text()
    failure_code = fields.Char(readonly=1)
    failure_reason = fields.Text(readonly=1)

    def action_run(self):
        for rec in self:
            threaded_calculation = threading.Thread(
                target=self.send_request, args=([[rec.id]]))
            threaded_calculation.start()

    def send_request(self, rec):
        time.sleep(5)
        with self.pool.cursor() as new_cr:
            _logger.info("BMP Request start")
            self = self.with_env(self.env(cr=new_cr))
            rec = self.env['bpm.request'].search([('id', 'in', rec)])
            bpm_url = self.env['ir.config_parameter'].sudo().get_param('bpm_url')
            rec.server_url = bpm_url
            access = get_bpm_access(bpm_url)

            if 'error' in access:
                rec.state = 'fail'
                rec.failure_reason = access['error']
            else:
                url = "{}{}".format(bpm_url, rec.route)
                body = eval(rec.body)
                payload = json.dumps(body)
                if access:
                    headers = {
                        'X-Bonita-API-Token': access['token'],
                        'Content-Type': 'application/json',
                        'Cookie': access['cookies']
                    }

                    try:
                        response = requests.request("POST", url, headers=headers, data=payload)
                        if response.status_code == 204:
                            _logger.info("[[BMP]] update payment success")
                            rec.state = 'done'
                        else:
                            _logger.info("[[BMP]] Update payment fail")
                            rec.state = 'fail'
                            rec.failure_reason = "Update Payment Fail"
                            rec.failure_code = response.status_code
                    except (
                            ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema,
                            requests.exceptions.Timeout,
                            requests.exceptions.HTTPError) as ex:
                        _logger.info("[[BMP]] update payment fail")
                        rec.state = 'fail'
                        rec.failure_reason = ex

            self._cr.savepoint()
        return {}

    # def send_request(self):
    #     for rec in self:
    #         bpm_url = self.env['ir.config_parameter'].sudo().get_param('bpm_url')
    #         rec.server_url = bpm_url
    #         access = get_bpm_access(bpm_url)
    #
    #         if 'error' in access:
    #             rec.state = 'fail'
    #             rec.failure_reason = access['error']
    #             return
    #
    #         url = "{}{}".format(bpm_url, rec.route)
    #         payload = json.dumps(rec.body)
    #         if access:
    #             headers = {
    #                 'X-Bonita-API-Token': access['token'],
    #                 'Content-Type': 'application/json',
    #                 'Cookie': access['cookies']
    #             }
    #
    #             try:
    #                 response = requests.request("POST", url, headers=headers, data=payload)
    #             except (
    #                     ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema,
    #                     requests.exceptions.Timeout,
    #                     requests.exceptions.HTTPError) as ex:
    #                 rec.state = 'fail'
    #                 rec.failure_reason = ex
    #                 return
    #
    #             if response.status_code == 204:
    #                 rec.state = 'done'
    #             else:
    #                 rec.state = 'fail'
    #                 rec.failure_code = response.status_code
    #                 rec.failure_reason = "Update Payment Fail"

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'
