from odoo import models, fields, api

class VisaExpirationIssue(models.Model):
    _name = 'visa.expiration.issue'
    _description = 'Visa Expiration Issue'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    visa_expiration_date = fields.Date(string="Visa Expiration Date")
    alert_date = fields.Date(string="Alert Date", compute="_compute_alert_date", store=True)

    @api.depends('visa_expiration_date')
    def _compute_alert_date(self):
        for record in self:
            if record.visa_expiration_date:
                record.alert_date = record.visa_expiration_date

