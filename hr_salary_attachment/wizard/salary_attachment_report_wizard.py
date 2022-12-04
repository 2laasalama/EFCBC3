from odoo import _, fields, models, api
from odoo.exceptions import UserError

MONTHS = [(1, 'يناير'),
          (2, 'فبراير'),
          (3, 'مارس'),
          (4, 'إبريل'),
          (5, 'مايو'),
          (6, 'يونيو'),
          (7, 'يوليو'),
          (8, 'أغسطس'),
          (9, 'سبتمبر'),
          (10, 'أكتوبر'),
          (11, 'نوفمبر'),
          (12, 'ديسمبر')]


class SalaryAttachmentReportWizard(models.TransientModel):
    _name = "salary.attachment.report.wizard"

    @api.depends('type')
    def _compute_name(self):
        for rec in self:
            if rec.type == 'rewards':
                rec.name = 'مكافأت للعاملين بالاتحاد'
            elif rec.type == 'vacation_allowance':
                rec.name = 'كشف العمل ايام العطلات'
            elif rec.type == 'night_allowance':
                rec.name = 'بدل اعاشة وسهر'
            else:
                rec.name = ''

    @api.model
    def _default_date_range(self):
        today = fields.Date.context_today(self)
        range = self.env['date.range'].search([('date_start', '<=', today), ('date_end', '>=', today)], limit=1)
        return range.id if range else False

    name = fields.Char(compute='_compute_name')
    type = fields.Selection([('rewards', 'rewards'),
                             ('vacation_allowance', 'Vacation Allowance'),
                             ('night_allowance', 'Night Allowance')], default='rewards', required=True)
    date_range_id = fields.Many2one("date.range", required=True, string="Month", default=_default_date_range)
    type_id = fields.Many2one("date.range.type", required=True, related='date_range_id.type_id')
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    date = fields.Date(default=fields.Date.context_today)
    month_ar = fields.Char(compute='_compute_month_ar', string='الشهر')

    vice_hr_manager = fields.Many2one('hr.employee', string='نائب رئيس الأمانة التنفيذية للموارد البشرية')
    vice_hr_manager_title = fields.Char(default='أستاذة')

    hr_consultant = fields.Many2one('hr.employee', string='مستشار (أ) للموارد البشرية')
    hr_consultant_title = fields.Char(default='محاسب')

    hr_manager = fields.Many2one('hr.employee', string='رئيس الأمانة التنفيذية للموارد البشرية')
    hr_manager_title = fields.Char(default='محاسب')

    general_secretary = fields.Many2one('hr.employee', string='الامين العام')
    general_secretary_title = fields.Char(default='محاسب')

    def print_report(self):
        return self.env.ref('hr_salary_attachment.salary_attachment_report').report_action(self.id)

    @api.depends('date_from')
    def _compute_month_ar(self):
        for rec in self:
            rec.month_ar = ''
            month = rec.date_from.month
            months = dict(MONTHS)
            rec.month_ar = months[month]

    def get_total_rewards(self):
        attachments = self.env['hr.salary.attachment'].search(
            [('deduction_type', '=', 'rewards'), ('state', '=', 'open'), ('date_start', '>=', self.date_from),
             ('date_start', '<=', self.date_to)])
        reward_amount = taxes = net = 0
        for rec in attachments:
            reward_amount += rec.reward_amount
            taxes += rec.taxes
            net += rec.net
        return {'reward': "%.2f" % round(reward_amount, 2), 'taxes': "%.2f" % round(taxes, 2),
                'net': "%.2f" % round(net, 2)}

    def get_rewards_report(self):
        vals = []
        attachments = self.env['hr.salary.attachment'].search(
            [('deduction_type', '=', 'rewards'), ('state', '=', 'open'), ('date_start', '>=', self.date_from),
             ('date_start', '<=', self.date_to)])
        for employee_id in attachments.mapped('employee_id'):
            employee_attachments = attachments.filtered(lambda l: l.employee_id == employee_id)

            reward_amount = taxes = net = 0
            for rec in employee_attachments:
                reward_amount += rec.reward_amount
                taxes += rec.taxes
                net += rec.net
            data = {
                'code': employee_id.code,
                'employee_name': employee_id.name,
                'salary': employee_attachments[0].contract_id.salary,
                'reward': "%.2f" % round(reward_amount, 2),
                'taxes': "%.2f" % round(taxes, 2),
                'net': "%.2f" % round(net, 2),
            }
            vals.append(data)

        return vals

    def get_vacation_allowance_report(self):
        vals = []
        attachments = self.env['hr.salary.attachment'].search(
            [('deduction_type', '=', 'vacation_allowance'), ('state', '=', 'open'),
             ('date_start', '>=', self.date_from),
             ('date_start', '<=', self.date_to)], order='date_start,employee_id')
        for attachment in attachments:
            data = {
                'code': attachment.employee_id.code,
                'employee_name': attachment.employee_id.name,
                'salary': attachment.contract_id.salary,
                'number_of_days': attachment.number_of_days,
                'overtime_amount_per_day': "%.2f" % round(attachment.overtime_amount_per_day, 2),
                'transportation_allowance_per_day': "%.2f" % round(attachment.transportation_allowance_per_day, 2),
                'taxes': "%.2f" % round(attachment.taxes, 2),
                'net': "%.2f" % round(attachment.net, 2),
            }
            vals.append(data)

        return vals

    def get_night_allowance_report(self):
        vals = []
        attachments = self.env['hr.salary.attachment'].search(
            [('deduction_type', '=', 'night_allowance'), ('state', '=', 'open'), ('date_start', '>=', self.date_from),
             ('date_start', '<=', self.date_to)])
        for employee_id in attachments.mapped('employee_id'):
            employee_attachments = attachments.filtered(lambda l: l.employee_id == employee_id)

            night_allowance = living_allowance = total_night_allowance = total_living_allowance = taxes = net = 0
            for rec in employee_attachments:
                night_allowance += rec.night_allowance
                living_allowance += rec.living_allowance
                total_night_allowance += rec.total_night_allowance
                total_living_allowance += rec.total_living_allowance
                taxes += rec.taxes
                net += rec.net
            contract = employee_attachments[0].contract_id
            data = {
                'code': employee_id.code,
                'employee_name': employee_id.name,
                'night_allowance': night_allowance,
                'living_allowance': living_allowance,
                'contract_night_allowance': contract.night_allowance,
                'contract_living_allowance': contract.living_allowance,
                'total_night_allowance': total_night_allowance,
                'total_living_allowance': total_living_allowance,
                'total': total_night_allowance + total_living_allowance,
                'taxes': "%.2f" % round(taxes, 2),
                'net': "%.2f" % round(net, 2),
            }
            vals.append(data)

        return vals

    def get_tabel_data(self):
        if self.type == 'rewards':
            return self.get_rewards_report()
        if self.type == 'vacation_allowance':
            return self.get_vacation_allowance_report()
        if self.type == 'night_allowance':
            return self.get_night_allowance_report()
