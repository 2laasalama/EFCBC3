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
    category_ids = fields.Many2many('hr.employee.category', related='employee_id.category_ids', readonly=True
                                    , string='المستوى الوظيفى')
    leave_ids = fields.One2many("hr.payslip.summary.leave", "summary_line_id", string='أجازات', readonly=True)
    fingerprint_absence = fields.Float(string='غياب بصمة', readonly=True)
    attendant_absence = fields.Float(string='أيام الغياب', readonly=True)
    total_lateness = fields.Float(string='تاخيرات بالدقيقة', readonly=True)
    excessive_leave_id = fields.Many2one('excessive.leave.line')
    excessive_leave_deduction = fields.Float(string='نسبة من الحافز والجهود والبدل', readonly=False)
    lateness_penalty_id = fields.Many2one('hr.lateness.penalty.report', string='تقرير عقوبة التاخيرات')
    penalty_absence = fields.Float()
    penalty_value = fields.Float()
    written_warning = fields.Boolean()
    penalty_days = fields.Float(string='أيام من الاجر اليومى')
    motivation_effort_days = fields.Float(string='ايام من الحافز والجهود والبدل', readonly=True)
    disciplinary_id = fields.Many2one('disciplinary.action')
    direct_motivation_effort = fields.Float(string='من الحافز والجهود مباشر', readonly=True)
    motivation_ratio = fields.Float(string='نسبة الحافز')
    effort_ratio = fields.Float(string='نسبة الجهود')

    def get_penalty_days(self, motivation_effort_days):
        for rec in self:
            penalty_days = 0
            total_absence = motivation_effort_days
            if total_absence > 0:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_first
            if total_absence > 0:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_second
            if total_absence > 0:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_third
            while total_absence > 0:
                total_absence -= 1
                penalty_days += rec.att_policy_id.absence_penalty_fourth
            return penalty_days

    def get_motivation_effort_days(self):
        for rec in self:
            motivation_effort_days = rec.attendant_absence + rec.penalty_absence
            return motivation_effort_days

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
                'total_lateness': attendance.tot_late * 60,
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

    def get_excessive_leave_report(self):
        self.excessive_leave_id.unlink()
        excessive_leave_id = self.env['excessive.leave.line'].create({
            'employee_id': self.employee_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        excessive_leave_id.action_update()

        return excessive_leave_id

    def get_direct_motivation_effort(self):
        actions = self.env['disciplinary.action'].search([('employee_name', '=', self.employee_id.id),
                                                          ('state', '=', 'action'),
                                                          '|', ('date_range_id', '=', self.date_range_id.id),
                                                          ('date_range_id2', '=', self.date_range_id.id)])
        actions_deduction = sum(action.deduction_percentage for action in actions)
        return actions_deduction

    def get_motivation_ratio(self, direct_motivation_effort, excessive_leave_deduction, motivation_effort_days):
        for rec in self:
            motivation_ratio = 0
            motivation_effort = 100 - direct_motivation_effort - excessive_leave_deduction
            if motivation_effort > 0:
                motivation_ratio = motivation_effort * rec.summary_id.motivation_ratio / 100
                motivation_ratio -= (5 * motivation_effort_days)
                motivation_ratio = motivation_ratio if motivation_ratio > 0 else 0
            return motivation_ratio

    def get_effort_ratio(self, direct_motivation_effort, excessive_leave_deduction, motivation_effort_days):
        for rec in self:
            effort_ratio = 0
            motivation_effort = 100 - direct_motivation_effort - excessive_leave_deduction
            if motivation_effort > 0:
                effort_ratio = motivation_effort * rec.summary_id.effort_ratio / 100
                effort_ratio -= (5 * motivation_effort_days)
                effort_ratio = effort_ratio if effort_ratio > 0 else 0
            return effort_ratio

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
            lateness_penalty = rec.get_lateness_penalty_report(rec.total_lateness / 60)
            excessive_leave_id = rec.get_excessive_leave_report()
            motivation_effort_days = rec.get_motivation_effort_days()
            direct_motivation_effort = self.get_direct_motivation_effort()
            excessive_leave_deduction = excessive_leave_id.deduction
            rec.update(
                {
                    'leave_ids': [(6, 0, leave_ids.ids)],
                    'fingerprint_absence': fingerprint_absence,
                    'penalty_absence': lateness_penalty.absence_days,
                    'penalty_value': lateness_penalty.penalty_value,
                    'motivation_effort_days': motivation_effort_days,
                    'written_warning': lateness_penalty.written_warning,
                    'excessive_leave_deduction': excessive_leave_deduction,
                    'direct_motivation_effort': self.get_direct_motivation_effort(),
                    'penalty_days': rec.get_penalty_days(motivation_effort_days),
                    'motivation_ratio': rec.get_motivation_ratio(direct_motivation_effort, excessive_leave_deduction,
                                                                 motivation_effort_days),
                    'effort_ratio': rec.get_effort_ratio(direct_motivation_effort, excessive_leave_deduction,
                                                         motivation_effort_days),
                }
            )
