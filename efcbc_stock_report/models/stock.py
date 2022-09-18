# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # analytic_account_id = fields.Many2one(
    #     string="Analytic Account",
    #     comodel_name="account.analytic.account",
    #     compute="_compute_analytic_account"
    # )

    #
    # @api.depends('move_lines')
    # def _compute_analytic_account(self):
    #     for rec in self:
    #         rec.analytic_account_id = False
    #         if rec.move_lines:
    #             rec.analytic_account_id = rec.move_lines[0].analytic_account_id

    def print_delivery_order_report(self):
        return self.env.ref('efcbc_stock_report.delivery_order_report').report_action(self.id)

    def print_receipt_order_report(self):
        return self.env.ref('efcbc_stock_report.receipt_order_report').report_action(self.id)

    def print_return_order_report(self):
        return self.env.ref('efcbc_stock_report.return_order_report').report_action(self.id)

    def print_check_receipt_report(self):
        return self.env.ref('efcbc_stock_report.check_receipt_report').report_action(self.id)
