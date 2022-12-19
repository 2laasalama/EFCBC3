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

    def open(self):
        self.ensure_one()
        self._compute_stock_report_by_location()
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Stock Location Move"),
            "context": {
                "search_default_groupby_product_id": 1,
            },
            "res_model": "stock.location.move",
            "domain": [("wiz_id", "=", self.id)],
        }
        return action

    def _compute_stock_report_by_location(self):
        self.ensure_one()
        move_line_ids = self.env["stock.move.line"].search(['|', ("location_id", "in", self.location_ids.ids),
                                                            ("location_dest_id", "in", self.location_ids.ids)])
        vals_list = []
        for move_line in move_line_ids:
            vals_list.append(
                {
                    "line_id": move_line.id,
                    "qty": move_line.qty_done if self.location_ids in move_line.location_id else -move_line.qty_done,
                    "wiz_id": self.id,
                }
            )
        self.env["stock.location.move"].sudo().create(vals_list)


class StockLocationMove(models.TransientModel):
    _name = "stock.location.move"
    _description = "Stock Location Move"

    wiz_id = fields.Many2one(comodel_name="stock.report.by.location.prepare")
    line_id = fields.Many2one("stock.move.line")
    reference = fields.Char(related='line_id.reference', store=True)
    state = fields.Selection(related='line_id.state', store=True, related_sudo=False)
    company_id = fields.Many2one('res.company', string='Company', related='line_id.company_id', store=True)
    product_id = fields.Many2one('product.product', 'Product', related="line_id.product_id", store=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', related="line_id.product_uom_id", store=True)
    product_qty = fields.Float('Real Reserved Quantity', related="line_id.product_qty", store=True)
    product_uom_qty = fields.Float('Reserved', digits='Product Unit of Measure', related="line_id.product_uom_qty",
                                   store=True)
    qty_done = fields.Float('Done', default=0.0, digits='Product Unit of Measure', related="line_id.qty_done",
                            store=True)
    qty = fields.Float()
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", related="line_id.lot_id",
        store=True)
    lot_name = fields.Char('Lot/Serial Number Name', related="line_id.lot_name", store=True)
    date = fields.Datetime('Date', related="line_id.date", store=True)
    owner_id = fields.Many2one(
        'res.partner', 'From Owner',
        check_company=True, related="line_id.owner_id", store=True,
        help="When validating the transfer, the products will be taken from this owner.")
    location_id = fields.Many2one('stock.location', 'From', related="line_id.location_id", store=True)
    location_dest_id = fields.Many2one('stock.location', 'To', related="line_id.location_dest_id", store=True)
