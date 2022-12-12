# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


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
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='compute_required_data')
    sequence = fields.Integer(readonly=True, string='م')
    employee_id = fields.Many2one('hr.employee', 'الموظف', required=True)
    employee_code = fields.Char(related='employee_id.code', string="Code")
    date = fields.Date(default=fields.Date.context_today, required=True)
    actual_amount = fields.Float(required=True)
