from odoo import models, fields

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    is_hr_department = fields.Boolean(string="HR Department", default=False)