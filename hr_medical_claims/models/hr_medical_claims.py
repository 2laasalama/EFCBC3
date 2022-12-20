# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HrMedicalClaims(models.Model):
    _name = "hr.medical.claims"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Medical Claims"

    name = fields.Char(required=True, default='New', readonly=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    partner_id = fields.Many2one('res.partner', required=True, domain=[('is_medical_provider', '=', True)],
                                 string='Provider')
    id_number = fields.Char(related='partner_id.id_number')
    provider_category = fields.Selection(
        [('hospital', 'Hospital'),
         ('clinic', 'Clinic'),
         ('laboratory', 'Laboratory'),
         ('radiology', 'Radiology'),
         ('pharmacy', 'Pharmacy'),
         ('other', 'Other')], related='partner_id.provider_category')

    line_ids = fields.One2many("hr.medical.claims.line", "claim_id", string="Lines", readonly=True,
                               states={"draft": [("readonly", False)]})
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], string="Status", index=True,
                             readonly=True,
                             copy=False, tracking=1, default="draft", )

    vice_hr_manager = fields.Many2one('hr.employee', string='نائب رئيس الأمانة التنفيذية للموارد البشرية')
    vice_hr_manager_title = fields.Char(default='أستاذة')

    hr_consultant = fields.Many2one('hr.employee', string='مستشار (أ) للموارد البشرية')
    hr_consultant_title = fields.Char(default='محاسب')

    hr_manager = fields.Many2one('hr.employee', string='رئيس الأمانة التنفيذية للموارد البشرية')
    hr_manager_title = fields.Char(default='محاسب')

    general_secretary = fields.Many2one('hr.employee', string='الامين العام')
    general_secretary_title = fields.Char(default='محاسب')

    @api.constrains('provider_category', 'line_ids')
    def check_rejected_line_ids(self):
        for rec in self:
            if rec.provider_category == 'other':
                if len(rec.line_ids) > 1:
                    raise ValidationError("Other claim accept only line.")

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.medical.claims') or _('New')
        return super(HrMedicalClaims, self).create(vals)

    def print_report(self):
        return self.env.ref('hr_medical_claims.medical_claims_report').report_action(self.id)

    def draft_action(self):
        return self.write({"state": "draft"})

    def close_action(self):
        return self.write({"state": "close"})

    def done_action(self):
        return self.write({"state": "done"})


class HrMedicalClaimsLine(models.Model):
    _name = "hr.medical.claims.line"

    claim_id = fields.Many2one('hr.medical.claims')
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], related='claim_id.state')
    provider_category = fields.Selection(
        [('hospital', 'Hospital'),
         ('clinic', 'Clinic'),
         ('laboratory', 'Laboratory'),
         ('radiology', 'Radiology'),
         ('pharmacy', 'Pharmacy'),
         ('other', 'Other')], related='claim_id.provider_category')
    date = fields.Date(default=fields.Date.context_today)
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='_compute_contract_id')
    sequence = fields.Integer(readonly=True, string='م')
    employee_id = fields.Many2one('hr.employee', 'الموظف', required=True)
    employee_code = fields.Char(related='employee_id.code', string="Code")
    service_type = fields.Selection(
        [('medical_examination ', 'Medical Examination '),
         ('medicine', 'Medicine'),
         ('lab_tests ', 'Lab Tests '),
         ('radiology', 'Radiology'),
         ('physiotherapy', 'Physiotherapy'),
         ('glasses', 'Optical Glasses'),
         ('lenses', 'Optical Lenses'),
         ('teeth', 'Teeth Crowns'),
         ('other', 'Other')], default='other')
    date = fields.Date(default=fields.Date.context_today, required=True)
    actual_amount = fields.Float(required=True)

    @api.depends('employee_id', 'date')
    def _compute_contract_id(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date, rec.date)
            rec.contract_id = False
            if contracts:
                rec.contract_id = contracts[0]

    @api.constrains('employee_id', 'service_type', 'date', 'actual_amount')
    def check_service_type(self):
        for rec in self:
            old_glasses = self.search([('employee_id', '=', rec.employee_id.id),
                                       ('service_type', '=', 'glasses'),
                                       ('id', '!=', rec.id)],
                                      order='date DESC',
                                      limit=1)
            if rec.service_type == 'glasses' and old_glasses:
                next_date = old_glasses.date + relativedelta(years=2)
                if rec.date < next_date:
                    raise ValidationError(
                        "Employee had optical glasses given on ({}), "
                        "Optical glasses only allowed after 2 years of prior service.".format(old_glasses.date))

            if rec.service_type == 'lenses' and old_glasses:
                next_date = old_glasses.date + relativedelta(years=1)
                if rec.date < next_date:
                    raise ValidationError(
                        "Employee had optical glasses given on ({}), "
                        "Optical Lenses only allowed after 1 year of Optical glasses service.".format(
                            old_glasses.date))

            if rec.service_type == 'lenses' and not old_glasses:
                raise ValidationError(
                    "Employee don't have optical glasses, "
                    "Optical Lenses only allowed after 1 year of Optical glasses service.")

            if rec.service_type == 'teeth' and not rec.contract_id:
                raise ValidationError(_('There is no valid contract for employee %s in Date %s' % (
                    rec.employee_id.name, rec.date)))

            if rec.service_type == 'teeth' and rec.contract_id:
                if rec.contract_id.teeth_crowns_start:
                    if rec.contract_id.teeth_crowns_start > rec.date:
                        raise ValidationError(
                            _('Request Date Must Be After Teeth Crowns Start On Employee Contract ({})'.format(
                                rec.contract_id.teeth_crowns_start)))
                    start_date, end_date = self.get_teeth_crowns_period(rec.contract_id.teeth_crowns_start, rec.date)
                    all_teeth_requests = self.search([('employee_id', '=', rec.employee_id.id),
                                                      ('service_type', '=', 'teeth'),
                                                      ('date', '>=', start_date),
                                                      ('date', '<=', end_date),
                                                      ])
                    total_teeth_amount = sum(x.actual_amount for x in all_teeth_requests)
                    if total_teeth_amount > 2500:
                        raise ValidationError(
                            _("Employee already/will be reaching the maximum limit for Teeth Crown Limit,"
                              " Utilized amount ({}) since ({})".format(total_teeth_amount, start_date)))
                else:
                    raise ValidationError(_('You Must define Teeth Crowns Start On Employee Contract.'))

    def get_teeth_crowns_period(self, teeth_crowns_start, request_date):
        start_date = teeth_crowns_start
        end_date = start_date + relativedelta(years=5)
        while end_date < request_date:
            start_date = end_date
            end_date = start_date + relativedelta(years=5)
        return start_date, end_date
