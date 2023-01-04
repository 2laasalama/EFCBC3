# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class DisciplineRule(models.Model):
    _name = 'disciplinary.rule'
    _description = 'Disciplinary Rule'

    name = fields.Char(default='disciplinary Rule')
    line_ids = fields.One2many('disciplinary.rule.line', 'rule_id')


class DisciplineRule(models.Model):
    _name = 'disciplinary.rule.line'
    _description = 'Disciplinary Rule Line'

    rule_id = fields.Many2one('disciplinary.rule')
    sequence = fields.Integer(default=1)
    days = fields.Integer(required=True, default=1)
    percentage = fields.Float(default=0)
    applied_on_months = fields.Integer(default=1)
    applied_on = fields.Selection([('one', 'One Month'), ('two', 'Two Months')], default='one', required=True, )

    @api.constrains('percentage')
    def _percentage_validation(self):
        for rec in self:
            if rec.percentage and not 0 <= rec.percentage <= 100:
                raise ValidationError(_('Invalid percentage value, must be between [0-100]'))
