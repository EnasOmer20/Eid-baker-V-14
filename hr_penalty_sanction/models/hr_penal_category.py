from odoo import models, fields

class HRPenalCategory(models.Model):
    _name = 'hr.penal.category'
    _description = 'Penal Sanction Category'

    name = fields.Char(string="Name", required=True)
    stage_ids = fields.One2many('hr.penal.stage', 'category_id', string="Stages")
    violation_ids = fields.One2many('hr.penal.violation', 'category_id', string="Violations")
