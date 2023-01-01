from odoo import models, api, fields


class ActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    is_stock_report = fields.Boolean()
