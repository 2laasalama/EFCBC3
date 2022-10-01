# -*- coding: utf-8 -*-

from odoo import models, api, fields


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    has_report = fields.Boolean()
    report_name = fields.Char()
    report_signature = fields.Char()
    origin_report = fields.Char('Origin')
    maintenance_company_report = fields.Char('Maintenance Company')
    partner_name = fields.Char("Partner")
    analytic_account_name = fields.Char("Analytic Account")
