# Copyright 2019-21 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class StockReportByLocationPrepare(models.TransientModel):
    _name = "stock.report.quantity.by.location.prepare"
    _description = "Stock Report Quantity By Location Prepare"

    def _default_date_range(self):
        active_id = self.env.context.get("active_id")
        return active_id

    picking_id = fields.Many2one(comodel_name="stock.picking", default=_default_date_range)
    location_id = fields.Many2one(comodel_name="stock.location", related='picking_id.location_dest_id')
    line_ids = fields.One2many('stock.report.quantity.by.location', 'wiz_id')

    def add_moves(self):
        print(self.line_ids)
        self.ensure_one()
        select_lines = self.line_ids.filtered(lambda l: l.select)
        if not select_lines:
            raise ValidationError(_('You must select at least one line to be added to picking.'))
        res = []
        for line in select_lines:
            vals = {
                "product_id": line.product_id.id,
                "name": line.product_id.name,
                "product_uom_qty": line.quantity_on_hand,
                "product_uom": line.uom_id.id,
                "location_id": self.picking_id.location_id.id,
                "location_dest_id": self.picking_id.location_dest_id.id,
                "picking_id": self.picking_id.id,
            }
            res.append((0, 0, vals))
        self.picking_id.move_ids_without_package = res
        return True

    @api.onchange('location_id')
    def onchange_location_id(self):
        if self.location_id:
            self._compute_stock_report_by_location()

    def _compute_stock_report_by_location(self):
        self.ensure_one()
        vals_list = []
        quants = self.env["stock.quant"].search(
            [("location_id", "child_of", [self.location_id.id])],

        )
        for quant in quants:
            if quant.quantity > 0:
                vals_list.append(
                    {
                        "product_id": quant.product_id.id,
                        "product_category_id": quant.product_id.categ_id.id,
                        "uom_id": quant.product_id.uom_id.id,
                        "quantity_on_hand": quant.quantity,
                        "quantity_reserved": quant.reserved_quantity,
                        "quantity_unreserved": quant.quantity - quant.reserved_quantity,
                        "location_id": self.location_id.id,
                        "wiz_id": self.id,
                        "default_code": quant.product_id.default_code,
                    }
                )
        self.env["stock.report.quantity.by.location"].create(vals_list)
        return


class StockReportQuantityByLocation(models.TransientModel):
    _name = "stock.report.quantity.by.location"
    _description = "Stock Report By Location"

    wiz_id = fields.Many2one(comodel_name="stock.report.quantity.by.location.prepare")
    select = fields.Boolean()
    product_id = fields.Many2one(comodel_name="product.product", required=True)
    product_category_id = fields.Many2one(
        comodel_name="product.category", string="Product Category"
    )
    location_id = fields.Many2one(comodel_name="stock.location", required=True)
    quantity_on_hand = fields.Float(string="Qty On Hand")
    quantity_reserved = fields.Float(string="Qty Reserved")
    quantity_unreserved = fields.Float(string="Qty Unreserved")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Product UoM")
    default_code = fields.Char("Internal Reference")
