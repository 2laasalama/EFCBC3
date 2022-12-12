# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ExcessiveLeavePolicy(models.Model):
    _name = 'excessive.leave.policy'
    _description = 'Excessive Leave Policy'

    name = fields.Char(default='Excessive Time-Off Policy')
    policy_lines = fields.One2many('excessive.leave.policy.line', 'policy_id')

    def check_deduction_rule(self, number_of_days):
        rules = self.env['excessive.leave.policy.line'].search([])
        if not rules:
            raise ValidationError(_("Three is no Excessive Leave Policy,\n You Can Configure it from"
                                    " [Time-off >> Configuration >> Excessive Time-Off Policy]."))

        rule = rules.filtered(lambda l: l.from_day <= number_of_days <= l.to_day)
        if not rule:
            rule = self.env['excessive.leave.policy.line'].search([], limit=1, order='to_day desc')

        return rule


class ExcessiveLeavePolicyLine(models.Model):
    _name = 'excessive.leave.policy.line'
    _description = 'Excessive Leave Policy Line'

    policy_id = fields.Many2one('excessive.leave.policy')
    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(required=True, default="Rule #1")
    from_day = fields.Float('Form', required=True)
    to_day = fields.Float('To', required=True)
    deduction = fields.Float('Deduction (%)', default=0, required=True)

    @api.constrains('deduction')
    def validate_deduction(self):
        for rec in self:
            if rec.deduction and not 0 <= rec.deduction <= 100:
                raise ValidationError(_("Deduction value Must Be percentage between [0-100]."))

    @api.constrains('from_day', 'to_day')
    def validate_days(self):
        for rec in self:
            if rec.from_day >= rec.to_day:
                raise ValidationError(_("Day [From] Must Be Greater than Day [To]."))
            lines = self.search(
                [('from_day', '<=', rec.from_day), ('to_day', '>=', rec.from_day),
                 ('id', '!=', rec.id)])
            if lines:
                raise ValidationError(_("Days can't overlap."))
