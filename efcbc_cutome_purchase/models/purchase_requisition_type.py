# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisitionType(models.Model):
    _inherit = 'purchase.requisition.type'

    name = fields.Char(string='Name')
    type = fields.Selection(
        string='Type',
        selection=[('public', 'مناقصة عامة'),
                   ('limited', 'مناقصة محدودة'),
                   ('direct', 'أمر مباشر')])
