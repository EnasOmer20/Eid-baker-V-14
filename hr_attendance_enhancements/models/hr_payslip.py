from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    late_value = fields.Float(string='Late Value', compute='_compute_late_value')
    overtime_value = fields.Float(string='Overtime Value', compute='_compute_overtime_value')

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_late_value(self):
        for payslip in self:
            late_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('approved_late', '=', True),
            ]).filtered(lambda a: a.check_in.date() >= payslip.date_from and a.check_out.date() <= payslip.date_to)

            late_total = 0.0
            for attendance in late_attendance:
                if attendance.approved_late:
                    late_total += attendance.late * (payslip.employee_id.contract_id.wage / 30)
            payslip.late_value = late_total

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_overtime_value(self):
        for payslip in self:

            overtime_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('approved_overtime', '=', True),
            ]).filtered(lambda a: a.check_in.date() >= payslip.date_from and a.check_out.date() <= payslip.date_to)

            overtime_total = 0.0
            for attendance in overtime_attendance:
                if attendance.approved_overtime:
                    overtime_total += attendance.overtime * (payslip.employee_id.contract_id.wage / 30)
                    overtime_rate = attendance._get_overtime_rate()
                    overtime_total *= overtime_rate
            payslip.overtime_value = overtime_total
