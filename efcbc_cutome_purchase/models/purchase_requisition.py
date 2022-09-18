# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    name = fields.Char('Purchase Request Number')
    reference_number = fields.Char('الرقم المرجعى', copy=False, readonly=True)
    deadline_status = fields.Selection([('urgent', 'Urgent'), ('not_urgent', 'Not Urgent')])
    ordering_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='الجهة الطالبة')
    public_partner_ids = fields.Many2many('res.partner', 'public_partner_rel', 'partner_id', 'public_id',
                                          string='الموردين')
    limited_partner_ids = fields.Many2many('res.partner', 'limited_partner_rel', 'partner_id', 'limited_id',
                                           string='الموردين')
    requisition_type = fields.Selection(selection=[('public', 'مناقصة عامة'),
                                                   ('limited', 'مناقصة محدودة'),
                                                   ('direct', 'أمر مباشر')], related='type_id.type')

    @api.model
    def create(self, vals):
        if not vals.get('reference_number'):
            vals['reference_number'] = self.env['ir.sequence'].next_by_code('purchase.requisition.ref') or _('New')
        return super(PurchaseRequisition, self).create(vals)


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    last_purchase_price = fields.Float('أخر سعر شراء', compute="_compute_last_purchase_price")
    purchase_reason = fields.Char('سبب الشراء')
    qty_available = fields.Float('رصيد المخزن', related='product_id.qty_available')

    @api.depends('product_id')
    def _compute_last_purchase_price(self):
        for rec in self:
            line = self.env['purchase.order.line'].search(
                [('product_id', '=', rec.product_id.id), ('order_id.state', '=', 'purchase'),
                 ('order_id.state', '=', 'purchase')], order='date_approve desc', limit=1)
            rec.last_purchase_price = line.price_unit if line else False
