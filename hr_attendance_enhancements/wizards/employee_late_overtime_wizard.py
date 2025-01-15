from odoo import models, fields, api

class EmployeeLateOvertimeWizard(models.TransientModel):
    _name = 'employee.late.overtime.wizard'
    _description = 'Employee Late and Overtime'

    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    def action_get_attendance(self):
        """Fetch attendances with late or overtime between selected dates and open the tree view"""
        domain = [
            ('check_in', '>=', self.date_start),
            ('check_out', '<=', self.date_end),
            '|',  # OR operator
            '&',  # AND condition for 'is_late' and 'approved_late'
            ('is_late', '=', True),
            ('approved_late', '!=', True),
            '&',  # AND condition for 'overtime' and 'approved_overtime'
            ('is_overtime', '=', True),
            ('approved_overtime', '!=', True)
        ]

        # Define the action for opening the tree view
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Employee Attendance',
            'res_model': 'hr.attendance',
            'view_mode': 'tree',
            'view_id': self.env.ref('hr_attendance_enhancements.view_hr_attendance_tree_with_buttons').id,
            # Reference to the default tree view for hr.attendance
            'domain': domain,  # Apply the domain for filtering records
            'target': 'current',  # Open in the current window
        }

        return action
