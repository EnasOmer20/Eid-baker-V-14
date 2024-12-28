from odoo import models, fields, api
from datetime import timedelta, datetime
import pytz

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    late = fields.Float(string='Late (Hours)', compute='_compute_late')
    overtime = fields.Float(string='Overtime (Hours)', compute='_compute_overtime')
    is_late = fields.Boolean(string='Late')
    is_overtime = fields.Boolean(string='Overtime')
    approved_late = fields.Boolean(string='Late Approved', default=False)
    approved_overtime = fields.Boolean(string='Overtime Approved', default=False)

    def _compute_late(self):
        """Compute late hours based on employee calendar"""
        for record in self:
            if record.employee_id and record.employee_id.resource_calendar_id:
                calendar = record.employee_id.resource_calendar_id
                planned_check_in, _ = self._get_planned_check_in_out(calendar, record.check_in)

                if record.check_in:
                    # Ensure check_in is timezone-aware
                    check_in = self._ensure_timezone_aware(record.check_in)
                    if check_in > planned_check_in:
                        record.late = (check_in - planned_check_in).total_seconds() / 3600.0
                        record.is_late = True
                    else:
                        record.late = 0.0

    def _compute_overtime(self):
        """Compute overtime hours based on employee calendar"""
        for record in self:
            if record.employee_id and record.employee_id.resource_calendar_id:
                calendar = record.employee_id.resource_calendar_id
                _, planned_check_out = self._get_planned_check_in_out(calendar, record.check_out)

                if record.check_out:
                    # Ensure check_out is timezone-aware
                    check_out = self._ensure_timezone_aware(record.check_out)
                    if check_out > planned_check_out:
                        record.overtime = (check_out - planned_check_out).total_seconds() / 3600.0
                        record.is_overtime = True
                    else:
                        record.overtime = 0.0

    def _get_planned_check_in_out(self, calendar, date):
        """Return the planned check-in and check-out times based on the employee calendar"""
        user_tz = self.env.user.tz or 'UTC'  # Get the user's timezone, default to UTC
        local_tz = pytz.timezone(user_tz)

        # Compute the start of the day in the user's timezone
        day_start = datetime(date.year, date.month, date.day)

        planned_intervals = calendar.attendance_ids
        if planned_intervals:
            # Sort intervals by hour_from to ensure proper order
            planned_intervals = sorted(planned_intervals, key=lambda x: x.hour_from)

            # Get the first interval for sign-in and the last for sign-out
            first_interval = planned_intervals[0]
            last_interval = planned_intervals[-1]

            # Calculate planned sign-in and sign-out times
            pl_sign_in_time = day_start + timedelta(hours=first_interval.hour_from)
            pl_sign_out_time = day_start + timedelta(hours=last_interval.hour_to)

            # Ensure datetimes are naive before localizing
            if pl_sign_in_time.tzinfo:
                pl_sign_in_time = pl_sign_in_time.replace(tzinfo=None)
            if pl_sign_out_time.tzinfo:
                pl_sign_out_time = pl_sign_out_time.replace(tzinfo=None)

            # Localize to user's timezone and convert to UTC
            pl_sign_in_time = local_tz.localize(pl_sign_in_time).astimezone(pytz.UTC)
            pl_sign_out_time = local_tz.localize(pl_sign_out_time).astimezone(pytz.UTC)

            return pl_sign_in_time, pl_sign_out_time

        # Default fallback times in UTC
        fallback_time = datetime.combine(date, datetime.strptime("09:00:00", "%H:%M:%S").time())
        return fallback_time, fallback_time + timedelta(hours=8)

    def _ensure_timezone_aware(self, naive_datetime):
        """Ensure the datetime is timezone-aware, converting it to UTC if necessary"""
        if naive_datetime.tzinfo is None:
            # If the datetime is naive, make it timezone-aware by assuming it is in UTC
            return pytz.UTC.localize(naive_datetime)
        return naive_datetime.astimezone(pytz.UTC)

    def action_approve_late(self):
        for record in self:
            record.approved_late = True

    def action_approve_overtime(self):
        for record in self:
            record.approved_overtime = True

    def _get_overtime_rate(self):
        """Determine the overtime rate based on workday or weekend"""
        day_of_week = self.check_out.weekday()  # Monday = 0, Sunday = 6
        employee_workdays = self.employee_id.resource_calendar_id.attendance_ids.mapped(lambda x: x.dayofweek)
        if day_of_week not in employee_workdays:  # weekend
            return self.employee_id.contract_id.holiday_hours
        else:  # workday
            return self.employee_id.contract_id.working_hours