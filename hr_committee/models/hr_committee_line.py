from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrCommitteeLine(models.Model):
    _name = "hr.committee.line"

    committee_id = fields.Many2one('hr.committee')
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("close", "Close")], related='committee_id.state')
    date_range_id = fields.Many2one("date.range", related='committee_id.date_range_id', required=True, string="Period")
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='compute_required_data')
    sequence = fields.Integer(readonly=True, string='م')
    employee_id = fields.Many2one('hr.employee', 'الموظف', required=True)
    employee_code = fields.Char(related='employee_id.code', string="Code")
    committees_count = fields.Integer()
    committees_category = fields.Float()
    allowance_amount = fields.Float(compute='_compute_allowance_amount')
    transportation_days = fields.Integer()
    transportation_Category = fields.Float()
    transportation_amount = fields.Float(compute='_compute_transportation_amount')
    total_earnings = fields.Float(compute='_compute_total_earnings')
    taxes = fields.Float(compute='_compute_taxes')
    net_pay = fields.Float(compute='_compute_net_pay')

    @api.depends('total_earnings', 'taxes')
    def _compute_net_pay(self):
        for rec in self:
            rec.net_pay = rec.total_earnings - rec.taxes

    @api.depends('total_earnings')
    def _compute_taxes(self):
        for rec in self:
            tax_ratio = self.env['ir.config_parameter'].sudo().get_param('efcbc_cutome_hr.tax_ratio')
            rec.taxes = rec.total_earnings * float(tax_ratio) / 100

    @api.depends('allowance_amount', 'transportation_amount')
    def _compute_total_earnings(self):
        for rec in self:
            rec.total_earnings = rec.allowance_amount + rec.transportation_amount

    @api.depends('transportation_days', 'transportation_Category')
    def _compute_transportation_amount(self):
        for rec in self:
            rec.transportation_amount = rec.transportation_days * rec.transportation_Category

    @api.depends('committees_count', 'committees_category')
    def _compute_allowance_amount(self):
        for rec in self:
            rec.allowance_amount = rec.committees_count * rec.committees_category

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_required_data(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date_from, rec.date_to)
            rec.contract_id = False
            if contracts:
                rec.contract_id = contracts[0]

    # @api.onchange('employee_id', 'date_from', 'date_to')
    # @api.constrains('employee_id', 'date_from', 'date_to')
    # def onchange_employee(self):
    #     for rec in self:
    #         if rec.employee_id and rec.date_from:
    #             contracts = rec.employee_id._get_contracts(rec.date_from, rec.date_to)
    #             if not contracts:
    #                 raise ValidationError(_('There is no valid contract for employee %s in period %s-%s' % (
    #                     rec.employee_id.name, rec.date_from, rec.date_to)))
