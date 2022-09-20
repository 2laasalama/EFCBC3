# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    payment_mode = fields.Many2one('payment.mode')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    payment_mode = fields.Many2one('payment.mode')
    executive_secretariat = fields.Many2one('hr.employee', 'Executive Secretariat for Purchasing and Stores')
    general_secretary = fields.Many2one('hr.employee', 'General Secretary')
    supply_date = fields.Date(compute='_compute_supply_date')
    supply_order_delivery = fields.Many2one('supply.order.delivery', 'تسليم أمر التوريد')
    committe_recommendation_date = fields.Date(string='تاريخ توصيه اللجان المختصه')
    committe_certified_date = fields.Date(string='تاريخ اعتماد السلطة المختصه')
    implementation_period = fields.Integer(string='مدة التنفيذ بالشهر')
    location_receipt_date = fields.Date(string='تاريخ استلام الموقع ')
    down_payment = fields.Monetary('الدفعة المقدمة')
    down_payment_rate = fields.Float('نسبة الدفعة المقدمة', compute='_compute_down_payment_rate')
    final_insurance_value = fields.Monetary('قيمة التامين النهائى')
    final_insurance_value_rate = fields.Float(compute='_compute_final_insurance_value_rate')

    @api.depends('final_insurance_value', 'amount_total')
    def _compute_final_insurance_value_rate(self):
        for rec in self:
            rec.final_insurance_value_rate = (rec.final_insurance_value / rec.amount_total) * 100

    @api.depends('down_payment', 'amount_total')
    def _compute_down_payment_rate(self):
        for rec in self:
            rec.down_payment_rate = (rec.down_payment / rec.amount_total) * 100

    def print_supply_order_report(self):
        return self.env.ref('efcbc_supply_order_report.supply_order_report').report_action(self.id)

    def print_work_assignment_order_report(self):
        return self.env.ref('efcbc_supply_order_report.work_assignment_order_report').report_action(self.id)

    def get_amount_total_in_text(self):
        return num2words(self.amount_total, lang='ar') + '  جنيه فقط لا غير '

    @api.depends('picking_ids')
    def _compute_supply_date(self):
        for rec in self:
            rec.supply_date = rec.picking_ids[0].scheduled_date if rec.picking_ids else False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    warranty_id = fields.Many2one('warranty.warranty', string='Warranty')


class Warranty(models.Model):
    _name = 'warranty.warranty'
    _description = 'Warranty'

    name = fields.Char(required=True)


class PaymentMode(models.Model):
    _name = 'payment.mode'
    _description = 'Payment Mode'

    name = fields.Char(required=True)


class SupplyOrderDelivery(models.Model):
    _name = 'supply.order.delivery'
    _description = 'Supply Order Delivery'

    name = fields.Char(required=True)
