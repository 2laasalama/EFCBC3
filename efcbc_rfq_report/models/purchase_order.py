# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    phone = fields.Char()
    email = fields.Char()


class PurchaseOrde(models.Model):
    _inherit = 'purchase.order'

    def print_quotation(self):
        return self.env.ref('efcbc_rfq_report.rfq_report').report_action(self)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    notes = fields.Char('الملاحظات')
