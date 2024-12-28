from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hiring_date = fields.Date(string="Hiring Date", required=True)
    end_of_service_ids = fields.One2many('hr.end.service', 'employee_id', string="End of Service")
    eof_count = fields.Integer(string="EOF Count", compute="_compute_eof_count")

    def _compute_eof_count(self):
        for employee in self:
            employee.eof_count = len(employee.end_of_service_ids)

    def action_view_eof(self):
        self.ensure_one()
        action = self.env.ref('hr_end_service_benefits.action_hr_end_service').read()[0]  # Replace `your_module_name` with the actual module name.
        action['domain'] = [('employee_id', '=', self.id)]
        action['context'] = {'default_employee_id': self.id}
        return action
