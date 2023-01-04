# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

import logging

LOGGER = logging.getLogger(__name__)


class PoApprovalLevel(models.Model):
    _name = 'po.approval.level'
    _description = 'Po Approval Level'

    name = fields.Char(string="Name", default='Approval Level', required=True)
    public_tender_rules = fields.One2many('po.approval.level.line', 'public_tender_id')
    limited_tender_rules = fields.One2many('po.approval.level.line', 'limited_tender_id')
    direct_order_rules = fields.One2many('po.approval.level.line', 'direct_order_id')


class PoApprovalLevelLine(models.Model):
    _name = 'po.approval.level.line'

    public_tender_id = fields.Many2one('po.approval.level')
    limited_tender_id = fields.Many2one('po.approval.level')
    direct_order_id = fields.Many2one('po.approval.level')
    sequence = fields.Integer()
    group_id = fields.Many2one('res.groups', string='المجموعة', required=True)
    supply_amount = fields.Float('توريدات')
    works_amount = fields.Float('اعمال')
    to_unlimited = fields.Boolean(string="بدون حد")

    @api.onchange('to_unlimited')
    def _onchange_user(self):
        if self.to_unlimited:
            self.works_amount = self.supply_amount = 0
