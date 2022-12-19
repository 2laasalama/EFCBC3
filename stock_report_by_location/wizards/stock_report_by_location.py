# Copyright 2019-21 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class StockReportByLocationPrepare(models.TransientModel):
    _name = "stock.report.by.location.prepare"
    _description = "Stock Report Quantity By Location Prepare"

    location_ids = fields.Many2many(comodel_name="stock.location", string="Locations", required=True)

    def open(self):
        self.ensure_one()
        domain = ['|', ("location_id", "in", self.location_ids.ids),
                  ("location_dest_id", "in", self.location_ids.ids)]
        result = self.env.ref('stock.stock_move_action')
        action_ref = result or False
        result = action_ref.read()[0]
        result['domain'] = str(domain)

        return result
