# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class InventoryAdjustmentsReport(models.AbstractModel):
    _name = 'report.efcbc_stock_report.inventory_adjustments_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        data['year'] =  fields.datetime.today().year
        docids = self.env['stock.quant'].browse(docids)
        return {
            'doc_model': self.env['res.company'],
            'data': data,
            'docs': docids,
        }
