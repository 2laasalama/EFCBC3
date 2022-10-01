# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _

import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TokenToken(models.Model):
    _name = 'token.token'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Token"
    _order = 'id desc, token_ref desc'

    def _get_default_sequence(self):
        if self.env.context.get('default_sequence'):
            return self.env.context.get('default_sequence')
        return self.env['token.sequence'].search([], limit=1).id

    name = fields.Char("Name", tracking=True)
    user_mobile = fields.Char("Contact No.", tracking=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    token_dept = fields.Many2one("department.department", string="Department", required=True, readonly="True")
    token_ref = fields.Char("Token Ref", required=True, copy=False,
                            readonly=True, index=True, default=lambda self: _('New'))
    token_day_number = fields.Char("Token No", copy=False,
                                   readonly=True, index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True,
        copy=False, index=True, tracking=True, default='draft')
    date = fields.Date(required=True, index=True, default=fields.Datetime.now)
    token_session = fields.Many2one(
        'token.session',
        string='Token Session',
        readonly=True,
        domain="[('state', '=', 'opened')]")
    queue_session = fields.Many2one(
        'queue.process',
        string='Queue Session',
        readonly=True)
    process_by = fields.Many2one(
        'res.users', string='Processed By',
        index=True,
        tracking=True
    )
    cust_query = fields.Text(string="Customer Query", tracking=True)
    feedback = fields.Text(string="Feedback", tracking=True)

    @api.model
    def create(self, vals):
        token = super(TokenToken, self).create(vals)
        token.token_ref = token.get_token()
        return token

    def get_token(self):
        count = self.env['token.token'].search_count(
            [('date', '=', self.date), ('token_dept', '=', self.token_dept.id)])
        return str(count).zfill(3)

    @api.constrains('token_dept', 'token_dept.capacity', 'token_dept.exception_ids')
    def check_available_tickets(self):
        for rec in self:
            available_tickets = rec.token_dept.get_available_tickets(rec.date)
            if available_tickets < 1:
                raise ValidationError(_('This Department is Fully Capacity in {}'.format(rec.date)))

    # @api.model
    # def _manage_seq(self, tokenObj):
    # tDate = tokenObj.date.date()
    # if tokenObj.token_ref == 'New' and tokenObj.token_session:
    #     tokenSession = tokenObj.token_session.config_id
    #     seq = tokenSession.token_seq
    #     newRef = seq.sequence_id.with_context(ir_sequence_date=tDate).next_by_id()
    #     tokenObj.token_ref = newRef
    # ctx = {
    #     'ir_sequence_date': tDate,
    #     'token_day': tDate,
    # }
    # tokenDay = self.env['ir.sequence'].with_context(ctx).next_by_code('token.perday')
    # tokenObj.token_day_number = tokenDay

    def do_done(self):
        self.write({'state': 'done'})
        return self.queue_process()

    def do_cancel(self):
        self.write({'state': 'cancel'})
        return self.queue_process()

    def queue_process(self):
        userSession = self.env['queue.process'].search(
            [('user_id', '=', self.env.uid), ('state', '=', 'opened')], limit=1
        )
        if userSession:
            return {
                'name': _('Session'),
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'queue.process',
                'res_id': userSession.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
            }
        return True
