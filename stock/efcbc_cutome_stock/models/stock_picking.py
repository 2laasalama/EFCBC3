# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_maintenance = fields.Boolean(related='picking_type_id.is_maintenance',)
    maintenance_company_id = fields.Many2one('res.partner', string='شركة الصيانة')
    fixed_assets = fields.Boolean(related='picking_type_id.fixed_assets', readonly=True)
    return_operation = fields.Boolean(related='picking_type_id.return_operation', readonly=True)
    scrap_committee_approved = fields.Boolean(copy=False)
    scrap_committee_approval = fields.Boolean(related='location_dest_id.scrap_committee_approval', copy=False)
    scrap_approval_id = fields.Many2one('scrap.committee.approval', copy=False)

    def _compute_show_validate(self):
        for rec in self:
            if rec.scrap_committee_approval and not rec.scrap_committee_approved:
                rec.show_validate = False
            else:
                return super(StockPicking, self)._compute_show_validate()

    def open_scrap_approval(self):
        self.ensure_one()
        approval = self.scrap_approval_id
        if not approval:
            approval = self.env['scrap.committee.approval'].create({
                'picking_id': self.id
            })
            self.scrap_approval_id = approval.id
        approval.check_committee_users()
        return {
            'name': _("موافقة لجنة الكهنه %s", self.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "context": {"create": False},
            'target': 'new',
            'res_model': 'scrap.committee.approval',
            'res_id': approval.id,
            'view_id': self.env.ref('efcbc_cutome_stock.scrap_committee_approval_view_form').id,
        }
