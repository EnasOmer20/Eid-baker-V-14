from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    holiday_hours = fields.Float(string='Holiday Hours')
    working_hours = fields.Float(string='Working Hours')

