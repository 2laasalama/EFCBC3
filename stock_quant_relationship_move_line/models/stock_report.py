from odoo import api, fields, models


class StockReport(models.Model):
    _inherit = "stock.report"

    analytic_account_id = fields.Many2one(related="picking_id.analytic_account_id", store=True)
    partner_id = fields.Many2one('res.partner',  string="الشخص/الشركة",related='picking_id.partner_id', store=True)
