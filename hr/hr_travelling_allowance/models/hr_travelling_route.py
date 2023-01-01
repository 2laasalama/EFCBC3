# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrTravellingRoute(models.Model):
    _name = "hr.travelling.route"

    location_from = fields.Many2one('hr.travelling.location', required=True)
    location_to = fields.Many2one('hr.travelling.location', required=True)
    amount = fields.Float(required=True)

    def name_get(self):
        result = []
        for account in self:
            name = account.location_from.name + ' - ' + account.location_to.name
            result.append((account.id, name))
        return result


class HrTravellingLocation(models.Model):
    _name = "hr.travelling.location"

    name = fields.Char(required=True)
