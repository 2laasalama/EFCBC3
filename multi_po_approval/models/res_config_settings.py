# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    use_multi_po_approval = fields.Boolean("Multi Purchase Order Approval", config_parameter='purchase.use_multi_po_approval')
    approval_id = fields.Many2one('po.approval.level',string='Configer Rules',config_parameter='purchase.approval_id')

