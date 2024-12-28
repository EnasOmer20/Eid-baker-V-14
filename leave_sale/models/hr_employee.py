from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    remaining_leaves = fields.Float(
        string="Remaining Annual Leaves",
        compute='_compute_remaining_leaves',
        readonly=True,
        help="The number of annual leave days the employee has remaining."
    )

    def _compute_remaining_leaves(self):
        for employee in self:
            # Calculate allocated days for annual leave
            allocated_days = sum(
                self.env['hr.leave.allocation'].search([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'validate'),
                    ('holiday_status_id.is_annual_leave', '=', True),
                ]).mapped('number_of_days')
            )
            # Calculate taken days for annual leave
            taken_days = sum(
                self.env['hr.leave'].search([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'validate'),
                    ('holiday_status_id.is_annual_leave', '=', True),
                ]).mapped('number_of_days')
            )
            # Compute remaining leaves
            employee.remaining_leaves = allocated_days - taken_days
