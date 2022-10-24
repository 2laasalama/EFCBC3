# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = 'hr.employee'

    lang = fields.Selection(default='ar_001')
    country_id = fields.Many2one(default=lambda self: self.env.ref('base.eg', False))
    country_of_birth = fields.Many2one(default=lambda self: self.env.ref('base.eg', False))
    identification_id = fields.Char(required=True)
    social_insurance_no = fields.Integer(required=True, groups="hr.group_hr_user", )
    gender = fields.Selection(required=True)
    birthday = fields.Date(required=True)
    hajj_granted = fields.Selection([('granted', "Granted"), ('not_granted', "Not Granted")],
                                    required=True, groups="hr.group_hr_user",
                                    default='not_granted')
    hajj_date = fields.Date(groups="hr.group_hr_user",)

    _sql_constraints = [
        ('identification_id_uniq', 'unique (identification_id)',
         "The Identification No must be unique, this one is already assigned to another employee."),

        ('social_insurance_no', 'unique (social_insurance_no)',
         "The Social Insurance No must be unique, this one is already assigned to another employee."),
    ]

    @api.onchange('identification_id')
    @api.constrains('identification_id')
    def _identification_id_validation(self):
        for rec in self:
            if rec.identification_id:
                if not rec.identification_id.isdigit():
                    raise ValidationError(_('Invalid Identification No, Accept only Numbers.'))
                if len(rec.identification_id) != 14:
                    raise ValidationError(_('Invalid Identification No, Length Must be 14 Digit.'))

    @api.onchange('social_insurance_no')
    @api.constrains('social_insurance_no')
    def _identification_social_insurance_no(self):
        for rec in self:
            if rec.social_insurance_no:
                if len(str(rec.social_insurance_no)) != 8:
                    raise ValidationError(_('Invalid Identification No, Length Must be 8 Digit.'))
