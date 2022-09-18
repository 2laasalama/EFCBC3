# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ("manager_director", "Manager Director"),
        ("general_secretary", "General Secretary"),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ])

    def manager_director_approve(self):
        for order in self:
            order.update({'state': 'manager_director'})
            group = self.env.ref('rfq_workflow.rfq_general_secretary_group')
            order.send_notifications(group)

    def general_secretary_approve(self):
        for order in self:
            order.update({'state': 'general_secretary'})

    @api.constrains('state')
    def onchange_state(self):
        for rec in self:
            if rec.state == 'draft':
                group = self.env.ref('rfq_workflow.rfq_manager_director_group')
                rec.send_notifications(group)

    def send_notifications(self, group):
        invite_template = self.env.ref('rfq_workflow.mail_template_rfq_workflow')
        group_users = group.users
        if group_users:
            email_values = {
                'recipient_ids': group_users.ids,
                'partner_ids': group_users.ids,
            }
            invite_template.send_mail(res_id=self.id, force_send=True, email_values=email_values)

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'general_secretary']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
