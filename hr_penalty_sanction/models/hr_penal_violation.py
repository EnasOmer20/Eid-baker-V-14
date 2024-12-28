from odoo import models, fields

class HRPenalViolation(models.Model):
    _name = 'hr.penal.violation'
    _description = 'Violation Lines'

    name = fields.Char(string="Violation Name", required=True)
    category_id = fields.Many2one('hr.penal.category', string="Category")
