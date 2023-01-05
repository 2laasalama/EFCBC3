from odoo import models, api, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    payment_order_sequence = fields.Many2one('ir.sequence')
    payment_permission_sequence = fields.Many2one('ir.sequence')
