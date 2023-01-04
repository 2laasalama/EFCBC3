# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_medical_provider = fields.Boolean()
    id_number = fields.Char()
    provider_category = fields.Selection(
        [('hospital', 'Hospital'),
         ('clinic', 'Clinic'),
         ('laboratory', 'Laboratory'),
         ('radiology', 'Radiology'),
         ('pharmacy', 'Pharmacy'),
         ('other', 'Other')])
