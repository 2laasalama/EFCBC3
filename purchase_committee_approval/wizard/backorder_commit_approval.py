# -*- coding: utf-8 -*-
from odoo import api, fields, models


class purchaseCommitteeapproval(models.Model):
    _name = 'backorder.committee.approval'
    _description = 'backorder Committee approval'

    name = fields.Char()
    purchase_id = fields.Many2one('purchase.order', 'Purchase')
    committee_decision = fields.Selection(selection=[('approve', 'Approve'), ('refuse', 'Refuse')])

    line_ids = fields.One2many('backorder.committee.approval.line', 'approval_id', "Approval Lines")
    quantity_line_ids = fields.One2many('backorder.quantity.approval.line', 'approval_id', "Quantity Lines")

    def action_approve(self):
        backorder = self.env['stock.picking'].search(
            [('purchase_order_id', '=', self.purchase_id), ('active', '=', False)])
        for move in backorder.move_lines:
            move.write({
                'quantity_done': move.purchase_line_id.backorder_accept_qty,
                'accept_purchase_qty': move.purchase_line_id.backorder_accept_qty
            })
        backorder.active = True

    def action_refuse(self):
        self.committee_decision = 'refuse'

    def check_quantity_approval(self):
        if self.purchase_id:
            for line in self.purchase_id.order_line:
                if not self.quantity_line_ids.filtered(lambda l: l.order_line_id == line):
                    self.env['backorder.quantity.approval.line'].create({
                        'order_line_id': line.id,
                        'approval_id': self.id
                    })

    def check_committee_users(self):
        if self.purchase_id.requisition_id:
            employees = self.purchase_id.requisition_id.purchase_committee_member_ids
            for employee in employees:
                if not self.line_ids.filtered(lambda l: l.employee_id == employee):
                    self.env['backorder.committee.approval.line'].create({
                        'employee_id': employee.id,
                        'approval_id': self.id
                    })


class purchaseCommitteeapprovalLine(models.Model):
    _name = 'backorder.committee.approval.line'
    _description = 'backorder Committee approval Line'

    name = fields.Char()
    approval_id = fields.Many2one('backorder.committee.approval')
    user_id = fields.Many2one('res.users', 'المستخدم', readonly=1)
    employee_id = fields.Many2one('hr.employee', 'الموظف', readonly=1)
    accept = fields.Boolean('موافقه')
    can_edit = fields.Boolean(compute="_compute_can_edit")

    def _compute_can_edit(self):
        for rec in self:
            rec.can_edit = False
            if self.env.user.has_group('purchase.group_purchase_manager'):
                rec.can_edit = True


class purchaseQuantityapprovalLine(models.Model):
    _name = 'backorder.quantity.approval.line'
    _description = 'Purchase Quantity approval Line'

    approval_id = fields.Many2one('backorder.committee.approval')
    order_line_id = fields.Many2one('purchase.order.line')
    product_id = fields.Many2one('product.product', related='order_line_id.product_id', string='الصنف', readonly=True)
    product_qty = fields.Float(string='الكمية المطلوبة', related='order_line_id.product_qty', readonly=True)
    qty_received = fields.Float(string='الكمية المستلمة', related='order_line_id.qty_received', readonly=True)
    qty_remainder = fields.Float(string='الكمية المتبقية', compute='_compute_qty_remainder', readonly=True)
    price_unit = fields.Float(string='سعر الوحدة', related='order_line_id.price_unit', readonly=True)
    accept = fields.Boolean(related='order_line_id.accept', string='موافقه', readonly=True)
    accept_qty = fields.Float(string='الكمية المقبولة', related='order_line_id.accept_qty', readonly=False)
    backorder_accept_qty = fields.Float(string='الكمية المقبولة', related='order_line_id.backorder_accept_qty',
                                        readonly=False)

    @api.depends('product_qty', 'qty_received')
    def _compute_qty_remainder(self):
        for rec in self:
            rec.qty_remainder = rec.product_qty - rec.qty_received
