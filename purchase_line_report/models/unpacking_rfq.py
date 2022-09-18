# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class UnpackingRFQ(models.Model):
    _name = 'unpacking.rfq'

    requisition_id = fields.Many2one('purchase.requisition')
    line_ids = fields.One2many('unpacking.rfq.line', 'unpacking_id')

    def get_partners(self):
        return self.line_ids.mapped('partner_id')

    def get_products(self):
        return self.line_ids.mapped('product_id')

    def get_product_lines(self, product_id):
        return self.line_ids.filtered(lambda x: x.product_id.id == product_id)

    def get_amount_totals(self, partner_id):
        return sum(x.price_total for x in self.line_ids.filtered(lambda x: x.partner_id.id == partner_id))

    def get_report_data(self, records):
        res = []
        order_lines = records.mapped('order_line')
        products = order_lines.mapped('product_id')
        for product in products:
            vals = {'product_name': product.name}
            for line in order_lines.filtered(lambda x: x.product_id.id == product.id):
                add = True
                for item in res:
                    if item['product_id'] == product.id and item['partner_id'] == line.order_id.partner_id.id:
                        add = False
                if add:
                    vals.update({
                        'unpacking_id': self.id,
                        'order_line_id': line.id,
                        'product_id': line.product_id.id,
                        'partner_id': line.partner_id.id,
                    })
                    res.append(vals)
                    vals = {}
        return res

    def action_print(self):
        return self.env.ref('purchase_line_report.purchase_line_xlsx').report_action(self.line_ids.ids)

    def print_unpacking_report(self):
        return self.env.ref('purchase_line_report.unpacking_report').report_action(self.id)

    def check_lines(self):
        values = self.get_report_data(self.requisition_id.purchase_ids)
        self.line_ids = False
        self.env['unpacking.rfq.line'].create(values)


class UnpackingRFQLine(models.Model):
    _name = 'unpacking.rfq.line'

    unpacking_id = fields.Many2one('unpacking.rfq')
    order_line_id = fields.Many2one('purchase.order.line')
    partner_id = fields.Many2one('res.partner', related='order_line_id.partner_id', string='المورد', readonly=True)
    product_id = fields.Many2one('product.product', related='order_line_id.product_id', string='الصنف', readonly=True)
    product_name = fields.Char(string='الصنف', readonly=True)
    price_unit = fields.Float(string='سعر الوحدة', related='order_line_id.price_unit', readonly=True)
    product_qty = fields.Float(string='الكمية', related='order_line_id.product_qty', readonly=True)
    price_subtotal = fields.Monetary(related='order_line_id.price_subtotal', string='الاجمالى', readonly=True)
    price_total = fields.Monetary(related='order_line_id.price_total', string=' الاجمالى شامل الضريبة', readonly=True)
    date_order = fields.Datetime(related='order_line_id.date_order', string=' تاريخ الاستلام', readonly=True)
    accept = fields.Boolean(related='order_line_id.accept', string='موافقه', readonly=False, )
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
