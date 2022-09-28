# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    committee_approval_id = fields.Many2one('purchase.committee.approval', copy=False)
    require_committee_approval = fields.Boolean(related='requisition_id.require_committee_approval', copy=False)
    require_rfq_unpacking = fields.Boolean(related='requisition_id.require_rfq_unpacking', copy=False)
    rfq_unpacking_approved = fields.Boolean(copy=False)
    rfq_unpacking_id = fields.Many2one('rfq.unpacking.approval', copy=False)
    start_workflow = fields.Boolean(compute='_compute_start_workflow', copy=False)
    backorder_approval_id = fields.Many2one('backorder.committee.approval', copy=False)
    require_backorder_committee = fields.Boolean(copy=False)

    def print_check_receipt_report(self):
        return self.env.ref('purchase_committee_approval.check_receipt_report').report_action(self.id)

    @api.depends('requisition_id')
    def _compute_require_committee_approval(self):
        for rec in self:
            rec.require_committee_approval = rec.requisition_id.require_committee_approval if rec.requisition_id else True

    @api.depends('state', 'require_rfq_unpacking', 'rfq_unpacking_approved')
    def _compute_start_workflow(self):
        for rec in self:
            rec.start_workflow = False
            if rec.state == 'draft':
                if rec.require_rfq_unpacking:
                    if rec.rfq_unpacking_approved:
                        rec.start_workflow = True
                    else:
                        rec.start_workflow = False
                else:
                    rec.start_workflow = True

    def action_confirm(self):
        if self.require_committee_approval:
            if self.committee_approval_id and self.committee_approval_id.committee_decision == 'approve':
                self.button_confirm()
            else:
                self.state = 'purchase'
        else:
            self.button_confirm()

    def open_committee_approval(self):
        self.ensure_one()
        approval = self.committee_approval_id
        if not approval:
            approval = self.env['purchase.committee.approval'].create({
                'purchase_id': self.id
            })
            self.committee_approval_id = approval.id
        approval.check_committee_users()
        approval.check_quantity_approval()
        return {
            'name': _("موافقة لجنة الاستلام رقم  %s", self.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "context": {"create": False},
            'target': 'new',
            'res_model': 'purchase.committee.approval',
            'res_id': approval.id,
            'view_id': self.env.ref('purchase_committee_approval.purchase_committee_approval_view_form').id,
        }

    def open_backorder_commit_approval(self):
        self.ensure_one()
        approval = self.backorder_approval_id
        if not approval:
            approval = self.env['backorder.committee.approval'].create({
                'purchase_id': self.id
            })
            self.backorder_approval_id = approval.id
        approval.check_committee_users()
        approval.check_quantity_approval()
        return {
            'name': _("موافقة لجنة المرتجعات "),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "context": {"create": False},
            'target': 'new',
            'res_model': 'backorder.committee.approval',
            'res_id': approval.id,
            'view_id': self.env.ref('purchase_committee_approval.backorder_committee_approval_view_form').id,
        }

    def open_rfq_unpacking_approval(self):
        self.ensure_one()
        approval = self.rfq_unpacking_id
        if not approval:
            approval = self.env['rfq.unpacking.approval'].create({
                'purchase_id': self.id
            })
            self.rfq_unpacking_id = approval.id
        approval.check_committee_users()
        return {
            'name': _("لجنة تفريع عروض الاسعار %s", self.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "context": {"create": False},
            'target': 'new',
            'res_model': 'rfq.unpacking.approval',
            'res_id': approval.id,
            'view_id': self.env.ref('purchase_committee_approval.rfq_unpacking_approval_view_form').id,
        }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    accept_qty = fields.Float(string='الكمية المقبولة')
    backorder_accept_qty = fields.Float(string='الكمية المقبولة')
    rejected_qty = fields.Float(compute='_compute_rejected_qty')
    rejected_qty_rate = fields.Float(compute='_compute_rejected_qty')

    @api.depends('accept_qty', 'product_qty')
    def _compute_rejected_qty(self):
        for rec in self:
            rec.rejected_qty = rec.product_qty - rec.accept_qty
            rec.rejected_qty_rate = (rec.rejected_qty / rec.product_qty) * 100
