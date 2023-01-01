from odoo import models
from odoo.addons.resource.models.resource import Intervals

from pytz import timezone
from datetime import datetime, time
from dateutil import rrule


class ResourceMixin(models.AbstractModel):
    _inherit = 'resource.mixin'

    def _get_work_days_data_batch(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        if self.env.context.get("exclude_holidays"):
            compute_leaves = False

        return super()._get_work_days_data_batch(from_datetime, to_datetime, compute_leaves=compute_leaves,
                                                 calendar=None, domain=None)
