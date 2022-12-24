# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrLeaveAccrualLevel(models.Model):
    _inherit = 'hr.leave.accrual.level'

    postpone_max_days = fields.Integer("Maximum amount of accruals to transfer",
                                       help="Set a maximum of days an allocation keeps at the end of the year. "
                                            "0 for no limit.")
