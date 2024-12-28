from odoo import models, fields, api
from dateutil.relativedelta import relativedelta  # Import for month calculations

class Employee(models.Model):
    _inherit = 'hr.employee'

    visa_expiration_alert_period = fields.Float(
        string="Visa Alert Period (Months)",
        default=1.0,  # Default alert period is 1 month
        help="Set the number of months before the visa expiration date to receive an alert."
    )

    def _check_visa_expiration(self):
        today = fields.Date.today()
        employees = self.search([('visa_expire', '!=', False)])
        for employee in employees:
            if employee.visa_expiration_alert_period > 0:
                # Calculate the alert date using months
                alert_date = employee.visa_expire - relativedelta(
                    months=int(employee.visa_expiration_alert_period)
                )
                if today >= alert_date:
                    # Check if already exists to avoid duplication
                    existing_issue = self.env['visa.expiration.issue'].search([
                        ('employee_id', '=', employee.id),
                        ('visa_expiration_date', '=', employee.visa_expire)
                    ], limit=1)

                    if not existing_issue:
                        self.env['visa.expiration.issue'].create({
                            'employee_id': employee.id,
                            'visa_expiration_date': employee.visa_expire,
                        })
