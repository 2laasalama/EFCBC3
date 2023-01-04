from odoo import models, fields, api, _

class account_journal(models.Model):

    _inherit = 'account.journal'

    payment_subtype = fields.Selection([('check',_('Check'))],string="Payment Subtype")

