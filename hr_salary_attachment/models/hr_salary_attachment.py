# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrSalaryAttachment(models.Model):
    _inherit = 'hr.salary.attachment'

    deduction_type = fields.Selection(
        selection_add=[('vacation_allowance', 'Vacation Allowance'),
                       ('night_allowance', 'Night Allowance')],
        ondelete={
            'vacation_allowance': 'set default',
            'night_allowance': 'set default',
        }
    )
    reward_amount = fields.Float()
    number_of_days = fields.Float()
    overtime_amount_per_day = fields.Float(compute='_compute_overtime_amount_per_day')
    transportation_allowance_per_day = fields.Float()
    night_allowance = fields.Float()
    living_allowance = fields.Float()
    total_night_allowance = fields.Float(compute='_total_living_night_allowance')
    total_living_allowance = fields.Float(compute='_total_living_night_allowance')
    total_living_night_allowance = fields.Float(compute='_total_living_night_allowance')
    taxes = fields.Float(compute='_compute_taxes')
    net = fields.Float(compute='_compute_net')
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='_compute_contract_id')
    basic_salary = fields.Float(compute='_compute_basic_salary')
    employee_code = fields.Char(related='employee_id.code', string="Code")

    @api.depends('basic_salary')
    def _compute_overtime_amount_per_day(self):
        for rec in self:
            rec.overtime_amount_per_day = (rec.basic_salary / 30) * 2

    @api.depends('contract_id')
    def _compute_basic_salary(self):
        for rec in self:
            if rec.contract_id:
                rec.basic_salary = rec.contract_id.basic_salary + rec.contract_id.variable_salary
            else:
                rec.basic_salary = 0

    @api.depends('night_allowance', 'living_allowance', 'contract_id')
    def _total_living_night_allowance(self):
        for rec in self:
            rec.total_night_allowance = rec.total_living_allowance = rec.total_living_night_allowance = False
            if rec.deduction_type == 'night_allowance' and rec.contract_id:
                rec.total_night_allowance = rec.night_allowance * rec.contract_id.night_allowance
                rec.total_living_allowance = rec.living_allowance * rec.contract_id.living_allowance
                rec.total_living_night_allowance = rec.total_night_allowance + rec.total_living_allowance

    @api.depends('deduction_type', 'number_of_days', 'overtime_amount_per_day',
                 'total_living_night_allowance')
    def _compute_taxes(self):
        for rec in self:
            rec.taxes = 0
            tax_ratio = float(self.env['ir.config_parameter'].sudo().get_param('efcbc_cutome_hr.tax_ratio')) / 100
            if rec.deduction_type == 'vacation_allowance':
                rec.taxes = tax_ratio * rec.number_of_days * rec.overtime_amount_per_day
            if rec.deduction_type == 'night_allowance':
                rec.taxes = tax_ratio * rec.total_living_night_allowance

    @api.depends('deduction_type', 'taxes', 'transportation_allowance_per_day')
    def _compute_net(self):
        for rec in self:
            rec.net = 0
            if rec.deduction_type == 'vacation_allowance':
                rec.net = (rec.number_of_days * rec.overtime_amount_per_day) - rec.taxes \
                          + rec.transportation_allowance_per_day
            if rec.deduction_type == 'night_allowance':
                rec.net = rec.total_living_night_allowance - rec.taxes

    @api.onchange('net')
    def onchange_net(self):
        self.monthly_amount = self.total_amount = self.net

    @api.constrains('deduction_type')
    def _check_amount_constraint(self):
        for rec in self:
            if rec.deduction_type == 'vacation_allowance' and rec.number_of_days <= 0:
                raise ValidationError(_('Number Of Days must be strictly positive.'))
            if rec.deduction_type == 'vacation_allowance' and rec.overtime_amount_per_day <= 0:
                raise ValidationError(_('Overtime Amount Per Day must be strictly positive.'))
            if rec.deduction_type == 'night_allowance' and rec.night_allowance <= 0 and rec.living_allowance <= 0:
                raise ValidationError(_('Night Allowance or Living Allowance must be strictly positive.'))

    @api.depends('deduction_type', 'date_end')
    def _compute_has_total_amount(self):
        for record in self:
            if record.deduction_type in ['vacation_allowance', 'night_allowance']:
                record.has_total_amount = False
            else:
                return super(HrSalaryAttachment, self)._compute_has_total_amount()

    @api.depends('employee_id', 'date_start')
    def _compute_contract_id(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date_start, rec.date_start)
            rec.contract_id = False
            if contracts:
                rec.contract_id = contracts[0]

    @api.onchange('employee_id', 'date_start')
    @api.constrains('employee_id', 'date_start', )
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id and rec.date_start and rec.deduction_type in ['vacation_allowance',
                                                                             'night_allowance']:
                contracts = rec.employee_id._get_contracts(rec.date_start, rec.date_start)
                if not contracts:
                    raise ValidationError(_('There is no valid contract for employee %s in Date %s' % (
                        rec.employee_id.name, rec.date_start)))
