# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
import calendar
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class Employee(models.Model):
    _inherit = 'hr.employee'

    lang = fields.Selection(default='ar_001')
    country_id = fields.Many2one(default=lambda self: self.env.ref('base.eg', False))
    country_of_birth = fields.Many2one(default=lambda self: self.env.ref('base.eg', False))
    identification_id = fields.Char(required=True)
    social_insurance_no = fields.Integer(required=True, groups="hr.group_hr_user", )
    gender = fields.Selection(required=True)
    birthday = fields.Date(required=True)
    hajj_granted_ids = fields.One2many('hajj.granted.line', 'employee_id',
                                       groups="hr.group_hr_user", )
    education_lines = fields.One2many('employee.education.line', 'employee_id',
                                      groups="hr.group_hr_user", )

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
    def _social_insurance_validation(self):
        for rec in self:
            if rec.social_insurance_no:
                if len(str(rec.social_insurance_no)) < 5:
                    raise ValidationError(_('Invalid Social Insurance No, Length Must be at least 5 Digit.'))


class HajjGrantedLine(models.Model):
    _name = 'hajj.granted.line'
    _description = 'Hajj Granted Line'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    type = fields.Selection([('umrah', "Umrah"), ('hajj', "Hajj"), ('other', "Other")],
                            required=True)
    name = fields.Char()
    date = fields.Date(default=fields.Date.context_today)
    amount = fields.Float()

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'umrah':
            self.name = _("Umrah")
        if self.type == 'hajj':
            self.name = _("Hajj")
        if self.type == 'other':
            self.name = False


class EmployeeEducationLine(models.Model):
    _name = 'employee.education.line'
    _description = 'Employee Education Line'

    def _get_years(self):
        return [(str(i), i) for i in
                range(1950, fields.Date.today().year, +1)]

    employee_id = fields.Many2one('hr.employee', string='Employee')
    certificate = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Certificate Level', default='other')
    study_field = fields.Char("Field of Study")
    year = fields.Selection(selection='_get_years')
