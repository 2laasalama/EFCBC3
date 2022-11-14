from odoo import models
from odoo.addons.resource.models.resource import Intervals

from pytz import timezone
from datetime import datetime, time
from dateutil import rrule


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _weekend_intervals(self, start_dt, end_dt, resource=None):
        """ Return the weekend intervals in the given datetime range.
            The returned intervals are expressed in the resource's timezone.
        """
        tz = timezone((resource or self).tz)
        start_dt = start_dt.astimezone(tz)
        end_dt = end_dt.astimezone(tz)
        start = start_dt.date()
        until = end_dt.date()
        result = []

        weekdays = [int(attendance.dayofweek) for attendance in self.attendance_ids]
        weekends = [d for d in range(7) if d not in weekdays]
        for day in rrule.rrule(rrule.DAILY, start, until=until, byweekday=weekends):
            result.append(
                (
                    datetime.combine(day, time.min).astimezone(tz),
                    datetime.combine(day, time.max).astimezone(tz), self
                ),
            )

        return result

    def _attendance_intervals_batch_exclude_weekends(self, start_dt, end_dt, intervals, resources, tz, res):
        for resource in resources:
            attendances = []
            for day in res[resource.id]:
                attendances.append(day)
            for day in self._weekend_intervals(start_dt, end_dt, resource):
                attendances.append(day)
            intervals[resource.id] = Intervals(attendances)

        return intervals

    def _attendance_intervals_batch(self, start_dt, end_dt, resources=None, domain=None, tz=None):
        print("_attendance_intervals_batch")
        res = super()._attendance_intervals_batch(start_dt=start_dt, end_dt=end_dt, resources=resources, domain=domain,
                                                  tz=tz)
        if not self.env.context.get("exclude_weekends") and resources:
            return self._attendance_intervals_batch_exclude_weekends(start_dt, end_dt, res, resources, tz, res)
        return res

    def get_work_hours_count(self, start_dt, end_dt, compute_leaves=True, domain=None):
        if self.env.context.get("exclude_holidays"):
            compute_leaves = False

        return super().get_work_hours_count(start_dt, end_dt, compute_leaves=compute_leaves, domain=None)
