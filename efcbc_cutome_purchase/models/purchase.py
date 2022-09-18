# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError

SELECTION_LIST = [
    ('normal', 'لا يوجد قرار'),
    ('done', 'موافقة'),
    ('blocked', 'رفض')
]


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sub_sequence = fields.Char('التسلسل الفرعى')
    total_supply_amount = fields.Float(compute='_compute_total_lines')
    total_works_amount = fields.Float(compute='_compute_total_lines')
    analytic_account_id = fields.Many2one('account.analytic.account', string='الجهة الطالبة')
    bid_opening_committee = fields.Selection(SELECTION_LIST, string='لجنة فتح المظاريف', copy=False)
    technical_committee = fields.Selection(SELECTION_LIST, string='لجنة فنية', copy=False)
    financial_committee = fields.Selection(SELECTION_LIST, string='لجنة المالية', copy=False)
    decision_committee = fields.Selection(SELECTION_LIST, string='لجنة البت', copy=False)
    requisition_type = fields.Selection(selection=[('public', 'مناقصة عامة'),
                                                   ('limited', 'مناقصة محدودة'),
                                                   ('direct', 'أمر مباشر')], related='requisition_id.requisition_type')

    show_committees = fields.Boolean(compute='_compute_show_committee')

    @api.depends('state', 'requisition_type')
    def _compute_show_committee(self):
        for rec in self:
            rec.show_committees = False
            if rec.requisition_type and rec.id:
                if rec.requisition_type == 'direct' and rec.state in ['purchase', 'done', 'cancel']:
                    rec.show_committees = False
                else:
                    rec.show_committees = True

    @api.onchange('requisition_id')
    def get_analytic_account_id(self):
        for rec in self:
            rec.analytic_account_id = rec.requisition_id.analytic_account_id

    @api.onchange('technical_committee')
    @api.constrains('technical_committee')
    def check_technical_committee(self):
        for rec in self:
            if rec.technical_committee == 'blocked':
                rec.button_cancel()

    @api.depends('order_line', 'order_line.product_id.main_type', 'order_line.price_total')
    def _compute_total_lines(self):
        for rec in self:
            rec.total_supply_amount = sum(
                line.price_total for line in rec.order_line.filtered(lambda l: l.product_id.main_type == 'supply'))
            rec.total_works_amount = sum(
                line.price_total for line in rec.order_line.filtered(lambda l: l.product_id.main_type == 'work'))

    @api.constrains('requisition_id')
    def check_purchase_sub_sequence(self):
        for rec in self:
            for id_index, purchase in enumerate(rec.requisition_id.purchase_ids.sorted(key='id')):
                purchase.sub_sequence = "{}/{}".format(rec.requisition_id.name, id_index + 1)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    partner_id = fields.Many2one('res.partner', string="الشخص/الشركة", related='order_id.partner_id')
    date_order = fields.Datetime(related='order_id.date_order')
    date_approve = fields.Datetime('Confirmation Date', related='order_id.date_approve', store=True)

    @api.constrains('product_id', 'order_id')
    def check_products(self):
        for rec in self:
            if rec.order_id.requisition_id:
                products = rec.order_id.requisition_id.line_ids.mapped('product_id')
                if rec.product_id not in products:
                    raise ValidationError(_("The Product [{}] not in Tender Products".format(rec.product_id.name)))
