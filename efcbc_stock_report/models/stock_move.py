# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    rejected_qty = fields.Float(compute='_compute_rejected_qty')
    rejected_qty_rate = fields.Float(compute='_compute_rejected_qty')

    @api.depends('quantity_done', 'product_qty')
    def _compute_rejected_qty(self):
        for rec in self:
            rec.rejected_qty = abs(rec.quantity_done - rec.product_qty)
            rec.rejected_qty_rate = (rec.rejected_qty / rec.product_qty) * 100
