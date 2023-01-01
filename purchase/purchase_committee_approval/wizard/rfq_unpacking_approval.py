# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RFQUnpackingApproval(models.Model):
    _name = 'rfq.unpacking.approval'
    _description = 'RFQ Unpacking Approval'

    name = fields.Char()
    purchase_id = fields.Many2one('purchase.order', 'Purchase')
    committee_decision = fields.Selection(selection=[('approve', 'Approve'), ('refuse', 'Refuse')])

    line_ids = fields.One2many('rfq.unpacking.approval.line', 'approval_id', "Approval Lines")

    def action_approve(self):
        self.purchase_id.rfq_unpacking_approved = True
        self.committee_decision = 'approve'

    def action_refuse(self):
        self.purchase_id.rfq_unpacking_approved = False
        self.committee_decision = 'refuse'

    def check_committee_users(self):
        if self.purchase_id.requisition_id:
            employees = self.purchase_id.requisition_id.committee_member_ids
            for employee in employees:
                if not self.line_ids.filtered(lambda l: l.employee_id == employee):
                    self.env['rfq.unpacking.approval.line'].create({
                        'employee_id': employee.id,
                        'approval_id': self.id
                    })


class RFQUnpackingApprovalLine(models.Model):
    _name = 'rfq.unpacking.approval.line'
    _description = 'Purchase Committee approval Line'

    name = fields.Char()
    approval_id = fields.Many2one('rfq.unpacking.approval')
    employee_id = fields.Many2one('hr.employee', 'الموظف', readonly=1)
    accept = fields.Boolean('موافقه')
    can_edit = fields.Boolean(compute="_compute_can_edit")

    def _compute_can_edit(self):
        for rec in self:
            rec.can_edit = False
            if self.env.user.has_group('purchase.group_purchase_manager'):
                rec.can_edit = True
