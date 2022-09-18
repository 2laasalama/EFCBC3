# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    unpacking_rfq_id = fields.Many2one('unpacking.rfq')

    def print_purchase_line_report(self):
        return self.env.ref('purchase_line_report.purchase_line_xlsx').report_action(self.purchase_ids.ids)



    def open_unpacking_rfq(self):
        self.ensure_one()
        unpacking_rfq_id = self.unpacking_rfq_id
        if not unpacking_rfq_id:
            unpacking_rfq_id = self.env['unpacking.rfq'].create({
                'requisition_id': self.id
            })
            self.unpacking_rfq_id = unpacking_rfq_id.id
        unpacking_rfq_id.check_lines()
        return {
            'name': _("تفريع عروض الاسعار %s", self.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "context": {"create": False},
            'target': 'new',
            'res_model': 'unpacking.rfq',
            'res_id': unpacking_rfq_id.id,
            'view_id': self.env.ref('purchase_line_report.unpacking_rfq_view_form').id,
        }