# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FinanceCommitteeApproval(models.Model):
    _name = 'finance.committee.approval'
    _description = 'Finance Committee Approval'

    name = fields.Char()
    picking_id = fields.Many2one('stock.picking', 'picking')
    committee_decision = fields.Selection(selection=[('approve', 'Approve'), ('refuse', 'Refuse')])

    line_ids = fields.One2many('finance.committee.approval.line', 'approval_id', "Approval Lines")

    def action_approve(self):
        self.picking_id.finance_committee_approved = True
        self.committee_decision = 'approve'

    def action_refuse(self):
        self.picking_id.finance_committee_approved = False
        self.committee_decision = 'refuse'

    def check_committee_users(self):
        if self.picking_id.finance_committee_approval:
            employees = self.picking_id.location_dest_id.finance_committee_member_ids
            for employee in employees:
                if not self.line_ids.filtered(lambda l: l.employee_id == employee):
                    self.env['finance.committee.approval.line'].create({
                        'employee_id': employee.id,
                        'approval_id': self.id
                    })


class RFQUnpackingApprovalLine(models.Model):
    _name = 'finance.committee.approval.line'

    name = fields.Char()
    approval_id = fields.Many2one('finance.committee.approval')
    employee_id = fields.Many2one('hr.employee', 'الموظف', readonly=1)
    accept = fields.Boolean('موافقه')
    can_edit = fields.Boolean(compute="_compute_can_edit")

    def _compute_can_edit(self):
        for rec in self:
            rec.can_edit = False
            if self.env.user.has_group('stock.group_stock_manager'):
                rec.can_edit = True
