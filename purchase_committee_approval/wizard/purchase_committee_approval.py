# -*- coding: utf-8 -*-
from odoo import api, fields, models


class purchaseCommitteeapproval(models.Model):
    _name = 'purchase.committee.approval'
    _description = 'Purchase Committee approval'

    name = fields.Char()
    purchase_id = fields.Many2one('purchase.order', 'Purchase')
    committee_decision = fields.Selection(selection=[('approve', 'Approve'), ('refuse', 'Refuse')])

    line_ids = fields.One2many('purchase.committee.approval.line', 'approval_id', "Approval Lines")

    def action_approve(self):
        if self.purchase_id.state == 'purchase':
            self.purchase_id.state = 'draft'
            self.purchase_id.button_confirm()
        self.committee_decision = 'approve'

    def action_refuse(self):
        self.committee_decision = 'refuse'

    # def check_committee_users(self):
    #     users = self.env.ref('purchase_committee_approval.purchase_committee_user_group').users
    #     for user in users:
    #         if not self.line_ids.filtered(lambda l: l.user_id == user):
    #             self.env['purchase.committee.approval.line'].create({
    #                 'user_id': user.id,
    #                 'employee_id': user.employee_id.id if user.employee_id else False,
    #                 'approval_id': self.id
    #             })

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
