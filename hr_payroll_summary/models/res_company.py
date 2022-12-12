# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    motivation_ratio = fields.Float(default=200)
    effort_ratio = fields.Float(default=100)
