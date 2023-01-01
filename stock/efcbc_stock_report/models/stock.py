# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    report_name = fields.Char(related='picking_type_id.report_name')
    report_signature = fields.Char(related='picking_type_id.report_signature')
    has_storekeeper_signature = fields.Boolean(related='picking_type_id.has_storekeeper_signature')
    has_report = fields.Boolean('ir.actions.report', related='picking_type_id.has_report')

    def print_stock_order_report(self):
        return self.env.ref('efcbc_stock_report.general_order_report').report_action(self.id)

    def print_delivery_order_report(self):
        return self.env.ref('efcbc_stock_report.delivery_order_report').report_action(self.id)

    def print_receipt_order_report(self):
        return self.env.ref('efcbc_stock_report.receipt_order_report').report_action(self.id)

    def print_return_order_report(self):
        return self.env.ref('efcbc_stock_report.return_order_report').report_action(self.id)

    def print_check_receipt_report(self):
        return self.env.ref('efcbc_stock_report.check_receipt_report').report_action(self.id)
