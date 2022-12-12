# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    uuid = fields.Char(readonly=True)
    id_number = fields.Char("ID Number")
    identification_type = fields.Char()
    country_id = fields.Many2one('res.country', string='Nationality')

    @api.constrains('uuid')
    def _check_uuid_constraint(self):
        """ rec code must be unique """
        for rec in self.filtered(lambda p: p.uuid):
            domain = [('id', '!=', rec.id), ('uuid', '=', rec.uuid)]
            if self.search(domain):
                raise ValidationError(_('uuid must be unique!'))
