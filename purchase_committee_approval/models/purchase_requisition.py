# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    require_committee_approval = fields.Boolean()
    purchase_committee_member_ids = fields.Many2many('hr.employee','employee_purchase_committee_rel', 'emp_id', 'purchase_id', string='أعضاء لجنة الاستلام')
    require_rfq_unpacking = fields.Boolean('يتطلب لجنه تفريغ عروض الاسعار')
    committee_member_ids = fields.Many2many('hr.employee', string='أعضاء اللجنة')
