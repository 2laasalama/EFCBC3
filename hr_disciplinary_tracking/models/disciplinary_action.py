# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    discipline_count = fields.Integer(compute="_compute_discipline_count")

    def _compute_discipline_count(self):
        all_actions = self.env['disciplinary.action'].read_group([
            ('employee_name', 'in', self.ids),
            ('state', '=', 'action'),
        ], fields=['employee_name'], groupby=['employee_name'])
        mapping = dict(
            [(action['employee_name'][0], action['employee_name_count']) for action in all_actions])
        for employee in self:
            employee.discipline_count = mapping.get(employee.id, 0)


class CategoryDiscipline(models.Model):
    _name = 'discipline.category'
    _description = 'Reason Category'

    # Discipline Categories

    code = fields.Char(string="Code", required=True, help="Category code")
    name = fields.Char(string="Name", required=True, help="Category name")
    category_type = fields.Selection(
        [('disciplinary', 'Disciplinary Category'), ('action', 'Action Category')],
        string="Category Type", help="Choose the category type disciplinary or action")
    description = fields.Text(string="Details", help="Details for this category")


class DisciplinaryAction(models.Model):
    _name = 'disciplinary.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Disciplinary Action"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('explain', 'Waiting Explanation'),
        ('submitted', 'Waiting Action'),
        ('action', 'Action Validated'),
        ('cancel', 'Cancelled'),

    ], default='draft', track_visibility='onchange')

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    employee_name = fields.Many2one('hr.employee', string='Employee', required=True,
                                    help="Employee name")
    department_name = fields.Many2one('hr.department', string='Department', required=True,
                                      help="Department name")
    discipline_reason = fields.Many2one('discipline.category', string='Reason', required=True,
                                        help="Choose a disciplinary reason")
    explanation = fields.Text(string="Explanation by Employee",
                              help='Employee have to give Explanation'
                                   'to manager about the violation of discipline')
    action = fields.Many2one('discipline.category', string="Action",
                             help="Choose an action for this disciplinary action")
    read_only = fields.Boolean(compute="get_user", default=True)
    warning_letter = fields.Html(string="Warning Letter")
    suspension_letter = fields.Html(string="Suspension Letter")
    termination_letter = fields.Html(string="Termination Letter")
    warning = fields.Boolean(default=False)
    action_details = fields.Text(string="Action Details", help="Give the details for this action")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments",
                                      help="Employee can submit any documents which supports their explanation")
    note = fields.Text(string="Internal Note")
    joined_date = fields.Date(string="Joined Date", help="Employee joining date")
    monetary_penalty = fields.Boolean(required=False)
    penalty_days = fields.Float()
    date_range_id = fields.Many2one("date.range", string="Applied On")
    date_range_id2 = fields.Many2one("date.range", string="Applied On")
    penalty_mode = fields.Selection(selection=[('days', 'Days'), ('amount', 'Amount')],
                                    default='days')
    action_type = fields.Selection(selection=[('warring', 'Warring Action'), ('deduction', 'Deduction From Salary')])
    action_lines = fields.One2many('disciplinary.action.line', 'disciplinary_id',
                                   string='Action Lines')
    disciplinary_rule_id = fields.Many2one('disciplinary.rule.line', compute="_compute_disciplinary_rule",
                                           string='Rule')

    disciplinary_rule_action = fields.Char(compute="_compute_disciplinary_rule_action", readonly=1)
    applied_on = fields.Selection([('one', 'One Month'), ('two', 'Two Months')],
                                  related='disciplinary_rule_id.applied_on')
    deduction_percentage = fields.Float(related='disciplinary_rule_id.percentage', store=True)

    def check_deduction_percentage(self):
        if self.action_type == 'deduction':
            if self.date_range_id:
                actions = self.search([('employee_name', '=', self.employee_name.id), ('state', '=', 'action'),
                                       '|', ('date_range_id', '=', self.date_range_id.id),
                                       ('date_range_id2', '=', self.date_range_id.id)])
                actions_deduction = sum(action.deduction_percentage for action in actions)
                if actions_deduction + self.deduction_percentage > 100:
                    raise ValidationError(
                        _("Sorry, You can not apply deduction on month ({}) because it fully deducted.".format(
                            self.date_range_id.name)))
            if self.date_range_id2:
                actions = self.search([('state', '=', 'action'), ('date_range_id', '=', self.date_range_id2.id),
                                       ('date_range_id2', '=', self.date_range_id2.id)])
                actions_deduction = sum(action.deduction_percentage for action in actions)
                if actions_deduction + self.deduction_percentage > 100:
                    raise ValidationError(
                        _("Sorry, You can not apply deduction on month {} because it fully deducted.".format(
                            self.date_range_id2.name)))

    @api.onchange('date_range_id', 'date_range_id2')
    @api.constrains('date_range_id', 'date_range_id2')
    def _check_date_range_ids(self):
        for rec in self:
            if rec.date_range_id and rec.date_range_id2:
                if rec.date_range_id == rec.date_range_id2:
                    raise ValidationError(_("You must select two different months."))
            today = fields.Date.context_today(self)
            if rec.date_range_id and rec.date_range_id.date_end < today:
                raise ValidationError(_("You can not select month before the current date."))
            if rec.date_range_id2 and rec.date_range_id2.date_end < today:
                raise ValidationError(_("You can not select month before the current date."))

    @api.depends('disciplinary_rule_id', 'penalty_days')
    def _compute_disciplinary_rule_action(self):
        for rec in self:
            action = ""
            if rec.disciplinary_rule_id:
                month = 'one month' if rec.disciplinary_rule_id.applied_on == 'one' else "two months"
                action = "TIP: {} days of penalty require to " \
                         "apply [{}] deduction percentage on {}".format(rec.penalty_days,
                                                                        rec.disciplinary_rule_id.percentage,
                                                                        month)
            rec.disciplinary_rule_action = action

    @api.depends('penalty_days')
    def _compute_disciplinary_rule(self):
        for rec in self:
            rule = False
            if rec.penalty_days > 0:
                for line in self.env['disciplinary.rule.line'].search([], order='days'):
                    rule = line
                    if rec.penalty_days <= line.days:
                        break

            rec.disciplinary_rule_id = rule

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('disciplinary.action')
        return super(DisciplinaryAction, self).create(vals)

    # Check the user is a manager or employee
    @api.depends('read_only')
    def get_user(self):

        if self.env.user.has_group('hr.group_hr_manager'):
            self.read_only = True
        else:
            self.read_only = False

    # Check the Action Selected

    @api.onchange('employee_name')
    def onchange_employee_name(self):

        department = self.env['hr.employee'].search([('name', '=', self.employee_name.name)])
        self.department_name = department.department_id.id

        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    @api.onchange('discipline_reason')
    def onchange_reason(self):
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    def assign_function(self):

        for rec in self:
            rec.state = 'explain'

    def cancel_function(self):
        for rec in self:
            rec.state = 'cancel'

    def set_to_function(self):
        for rec in self:
            rec.state = 'draft'

    def action_function(self):
        for rec in self:
            if not rec.action_type:
                raise ValidationError(_('You have to select Action Type !!'))
            if rec.action_type == 'warring' and not rec.action:
                raise ValidationError(_('You have to select an Action !!'))

            if rec.action_type == 'deduction' and not rec.penalty_days or not rec.date_range_id:
                raise ValidationError(_('You have to Enter Penalty Days!!'))

            rec.check_deduction_percentage()
            rec.state = 'action'

    def explanation_function(self):
        for rec in self:

            if not rec.explanation:
                raise ValidationError(_('You must give an explanation !!'))

        self.write({
            'state': 'submitted'
        })


class DisciplinaryActionLine(models.Model):
    _name = 'disciplinary.action.line'

    def _get_years(self):
        return [(str(i), i) for i in
                range(fields.Date.today().year, fields.Date.today().year + 10, +1)]

    def _get_months(self):
        return [(str(i), i) for i in
                range(1, 13, +1)]

    disciplinary_id = fields.Many2one('disciplinary.action', string='Disciplinary')
    days = fields.Float()
    amount = fields.Float()
    month = fields.Selection(selection='_get_months', string='Applied Month', required=True,
                             default=lambda x: str(fields.Date.today().month))
    year = fields.Selection(
        selection='_get_years', string='Applied Year', required=True,
        default=lambda x: str(fields.Date.today().year))
