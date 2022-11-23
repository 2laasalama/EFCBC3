from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrPayslipsummaryLine(models.Model):
    _name = "hr.payslip.summary.line"

    summary_id = fields.Many2one('hr.payslip.summary')
    date_range_id = fields.Many2one("date.range", required=True, string="Period", related='summary_id.date_range_id')
    date_from = fields.Date(string="Date From", required=True, related='date_range_id.date_start')
    date_to = fields.Date(string="Date To", required=True, related='date_range_id.date_end')
    att_policy_id = fields.Many2one('hr.attendance.policy', string="Attendance Policy", compute='compute_required_data')
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='compute_required_data')
    sequence = fields.Integer(readonly=True, string='م')
    employee_id = fields.Many2one('hr.employee', 'الموظف', required=True, readonly=True)
    category_ids = fields.Many2many('hr.employee.category', related='employee_id.category_ids',
                                    string='المستوى الوظيفى',
                                    readonly=True)
    leave_ids = fields.One2many("hr.payslip.summary.leave", "summary_line_id", string='أجازات', readonly=True)
    fingerprint_absence = fields.Float(string='غياب بصمة', readonly=True)
    attendant_absence = fields.Float(string='أيام الغياب', readonly=True)
    total_lateness = fields.Float(string='تاخيرات بالدقيقة', readonly=True)
    lateness_penalty_id = fields.Many2one('hr.lateness.penalty.report', string='تقرير عقوبة التاخيرات')
    penalty_absence = fields.Float(related='lateness_penalty_id.absence_days', readonly=True)
    penalty_value = fields.Float(related='lateness_penalty_id.penalty_value', readonly=True)
    penalty_days = fields.Float(string='أيام من الاجر اليومى', compute='_get_lateness_penalty', readonly=True)
    motivation_effort_days = fields.Float(compute='_compute_motivation_effort_days',
                                          string='ايام من الحافز والجهود والبدل', readonly=True)

    written_warning = fields.Boolean(related='lateness_penalty_id.written_warning', )

    @api.depends('motivation_effort_days', 'penalty_days', 'att_policy_id')
    def _get_lateness_penalty(self):
        for rec in self:
            penalty_days = rec.penalty_days
            total_absence = rec.motivation_effort_days
            if total_absence > 1:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_first
            if total_absence > 1:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_second
            if total_absence > 1:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_third
            while total_absence > 1:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_fourth
            rec.penalty_days = penalty_days

    @api.depends('attendant_absence', 'penalty_absence')
    def _compute_motivation_effort_days(self):
        for rec in self:
            rec.motivation_effort_days = rec.attendant_absence + rec.penalty_absence

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_required_data(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date_from, rec.date_to)
            rec.contract_id = rec.att_policy_id = False
            if contracts:
                rec.contract_id = contracts[0]
                rec.att_policy_id = contracts[0].att_policy_id

    @api.onchange('employee_id', 'date_from', 'date_to')
    @api.constrains('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        for rec in self:
            contracts = rec.employee_id._get_contracts(rec.date_from, rec.date_to)
            if not contracts:
                raise ValidationError(_('There is no valid contract for employee %s' % rec.employee_id.name))
            if not contracts[0].att_policy_id:
                raise ValidationError(_("Employee %s does not have attendance policy" % rec.employee_id.name))

    def get_fingerprint_absence(self, employee, date_from, date_to):
        attendances = self.env['hr.attendance'].search(
            [('employee_id', '=', employee.id), ('date', '>=', date_from),
             ('date', '<=', date_to)]).mapped('date')
        return len(attendances)

    def get_leave_summary(self, employee, date_from, date_to):
        vals = []
        all_leaves = self.env['hr.leave'].search([('employee_id', '=', employee.id), ('date_from', '>=', date_from),
                                                  ('date_from', '<=', date_to)])

        for leave_type in self.env['hr.leave.type'].search([('payroll_summary', '=', True)]):
            number_of_days = sum(
                all_leaves.filtered(lambda l: l.holiday_status_id == leave_type).mapped('number_of_days'))
            vals.append({
                'number_of_days': number_of_days,
                'holiday_status_id': leave_type.id
            })

        return vals

    def get_attendance_sheet_data(self):
        attendance_obj = self.env['attendance.sheet']
        attendance = attendance_obj.new({'employee_id': self.employee_id.id,
                                         'date_from': self.date_from,
                                         'date_to': self.date_to,
                                         })
        attendance.onchange_employee()
        attendance.get_attendances()
        self.update(
            {
                'total_lateness': attendance.tot_late,
                'attendant_absence': attendance.no_absence
            }
        )

    def get_lateness_penalty_report(self, total_lateness):
        self.lateness_penalty_id.unlink()
        lateness_penalty_id = self.env['hr.lateness.penalty.report'].create({'employee_id': self.employee_id.id,
                                                                             'date_range_id': self.date_range_id.id,
                                                                             'att_policy_id': self.att_policy_id.id,
                                                                             'total_lateness': total_lateness,
                                                                             })

        return lateness_penalty_id

    def compute_sheet(self):
        for rec in self:
            # get number of leaves
            leave_summary_vals = rec.get_leave_summary(rec.employee_id, rec.date_from, rec.date_to)
            leave_ids = self.env['hr.payslip.summary.leave'].create(leave_summary_vals)
            rec.leave_ids.unlink()
            # get number of absences
            fingerprint_absence = rec.get_fingerprint_absence(rec.employee_id, rec.date_from, rec.date_to)
            # get number of lateness
            rec.get_attendance_sheet_data()
            lateness_penalty = self.get_lateness_penalty_report(rec.total_lateness / 60)
            rec.update(
                {
                    'leave_ids': [(6, 0, leave_ids.ids)],
                    'fingerprint_absence': fingerprint_absence,
                    'lateness_penalty_id': lateness_penalty.id,
                }
            )
