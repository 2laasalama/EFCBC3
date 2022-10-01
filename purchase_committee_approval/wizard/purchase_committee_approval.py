# -*- coding: utf-8 -*-
from odoo import api, fields, models


class purchaseCommitteeapproval(models.Model):
    _name = 'purchase.committee.approval'
    _description = 'Purchase Committee approval'

    name = fields.Char()
    purchase_id = fields.Many2one('purchase.order', 'Purchase')
    committee_decision = fields.Selection(selection=[('approve', 'Approve'), ('refuse', 'Refuse')])

    line_ids = fields.One2many('purchase.committee.approval.line', 'approval_id', "Approval Lines")
    quantity_line_ids = fields.One2many('purchase.quantity.approval.line', 'approval_id', "Quantity Lines")
    show_backorder = fields.Boolean(compute='_compute_show_backorder', default=False)

    @api.depends('quantity_line_ids', 'quantity_line_ids.qty_received')
    def _compute_show_backorder(self):
        for rec in self:
            rec.show_backorder = False
            for line in rec.quantity_line_ids.filtered(lambda p: p.qty_received > 0):
                if line.qty_received < line.product_qty:
                    rec.show_backorder = True
                    return

    def action_approve(self):
        if self.purchase_id.state == 'purchase':
            self.purchase_id.state = 'draft'
            self.purchase_id.button_confirm()
        self.committee_decision = 'approve'

    def action_refuse(self):
        self.committee_decision = 'refuse'

    def create_backorder(self):
        self.purchase_id.require_backorder_committee = True

    def check_quantity_approval(self):
        if self.purchase_id:
            for line in self.purchase_id.order_line:
                if not self.quantity_line_ids.filtered(lambda l: l.order_line_id == line):
                    self.env['purchase.quantity.approval.line'].create({
                        'order_line_id': line.id,
                        'approval_id': self.id
                    })

    def check_committee_users(self):
        if self.purchase_id.requisition_id:
            employees = self.purchase_id.requisition_id.purchase_committee_member_ids
            for employee in employees:
                if not self.line_ids.filtered(lambda l: l.employee_id == employee):
                    self.env['purchase.committee.approval.line'].create({
                        'employee_id': employee.id,
                        'approval_id': self.id
                    })


class purchaseCommitteeapprovalLine(models.Model):
    _name = 'purchase.committee.approval.line'
    _description = 'Purchase Committee approval Line'

    name = fields.Char()
    approval_id = fields.Many2one('purchase.committee.approval')
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
    _name = 'purchase.quantity.approval.line'
    _description = 'Purchase Quantity approval Line'

    approval_id = fields.Many2one('purchase.committee.approval')
    order_line_id = fields.Many2one('purchase.order.line')
    product_id = fields.Many2one('product.product', related='order_line_id.product_id', string='الصنف', readonly=True)
    product_qty = fields.Float(string='الكمية المطلوبة', related='order_line_id.product_qty', readonly=True)
    qty_received = fields.Float(string='الكمية المستلمة', related='order_line_id.qty_received', readonly=True)
    price_unit = fields.Float(string='سعر الوحدة', related='order_line_id.price_unit', readonly=True)
    accept = fields.Boolean(related='order_line_id.accept', string='موافقه', readonly=True)
    accept_qty = fields.Float(string='الكمية المقبولة', related='order_line_id.accept_qty', readonly=False)
