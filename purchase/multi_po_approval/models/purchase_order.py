# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError

from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('state')
    def check_approvals_rules(self):
        for rec in self:
            use_multi_po_approval = self.env['ir.config_parameter'].sudo().get_param(
                'purchase.use_multi_po_approval',
                False)
            approval_id = self.env['ir.config_parameter'].sudo().get_param('purchase.approval_id', False)

            if use_multi_po_approval and approval_id and rec.requisition_id and rec.state == 'purchase':
                approval_id = self.env['po.approval.level'].browse(int(approval_id))
                if rec.requisition_id.requisition_type == 'public':
                    self.check_user_limition(approval_id.public_tender_rules)
                elif rec.requisition_id.requisition_type == 'limited':
                    self.check_user_limition(approval_id.limited_tender_rules)
                elif rec.requisition_id.requisition_type == 'direct':
                    self.check_user_limition(approval_id.direct_order_rules)

    def check_user_limition(self, lines):
        unlimited_line = lines.filtered(lambda l: l.to_unlimited)
        if unlimited_line.group_id in self.env.user.groups_id:
            return
        self.check_supply_lines(lines)
        self.check_works_lines(lines)

    def check_supply_lines(self, lines):
        for line in lines.filtered(lambda l: not l.to_unlimited).sorted(key='supply_amount', reverse=True):
            if self.total_supply_amount <= line.supply_amount and line.group_id in self.env.user.groups_id:
                return

        raise ValidationError(
            'لا يمكنك الموافقة على عرض السعر . لانك لا تملك  صلاحية موافقة على  هذا النوع من عروض الاسعار')

    def check_works_lines(self, lines):
        for line in lines.filtered(lambda l: not l.to_unlimited).sorted(key='works_amount', reverse=True):
            if self.total_works_amount <= line.works_amount and line.group_id in self.env.user.groups_id:
                return

        raise ValidationError(
            'لا يمكنك الموافقة على عرض السعر . لانك لا تملك  صلاحية موافقة على  هذا النوع من عروض الاسعار')
