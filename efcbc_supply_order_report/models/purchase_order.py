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
    down_payment = fields.Monetary(string='الدفعة المقدمة', compute='_compute_down_payment')
    down_payment_rate = fields.Float(string='نسبة الدفعة المقدمة')
    final_insurance_value = fields.Monetary(string='قيمة التامين النهائى',
                                            compute='_compute_final_insurance_value')
    final_insurance_value_rate = fields.Float(string='نسبة التامين النهائى')

    @api.depends('final_insurance_value_rate', 'amount_total')
    def _compute_final_insurance_value(self):
        for rec in self:
            rec.final_insurance_value = (rec.final_insurance_value_rate / 100) * rec.amount_total

    @api.depends('down_payment_rate', 'amount_total')
    def _compute_down_payment(self):
        for rec in self:
            rec.down_payment = (rec.down_payment_rate / 100) * rec.amount_total

    def print_supply_order_report(self):
        return self.env.ref('efcbc_supply_order_report.supply_order_report').report_action(self.id)

    def print_work_assignment_order_report(self):
        return self.env.ref('efcbc_supply_order_report.work_assignment_order_report').report_action(self.id)

    def print_supply_work_order_report(self):
        return self.env.ref('efcbc_supply_order_report.supply_work_order_report').report_action(self.id)

    def get_amount_total_in_text(self):
        return self.currency_id.with_context(lang='ar_001').amount_to_text(self.amount_total) + ' فقط لا غير '

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
