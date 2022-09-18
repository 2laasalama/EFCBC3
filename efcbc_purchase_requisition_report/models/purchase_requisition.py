# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    analytic_account_id = fields.Many2one('account.analytic.account', 'الجهة الطالبة')
