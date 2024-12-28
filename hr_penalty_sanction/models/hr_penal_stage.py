from odoo import models, fields

class HRPenalStage(models.Model):
    _name = 'hr.penal.stage'
    _description = 'Penal Sanction Stage'

    name = fields.Char(string="Stage Name", required=True)
    category_id = fields.Many2one('hr.penal.category', string="Category")
    warning = fields.Boolean(string="Warning")
    salary_deduction = fields.Boolean(string="Salary Deduction")
    deduction_type = fields.Selection([('fixed', 'Fixed'), ('per_day', 'Per Day')], string="Deduction Type")
    termination = fields.Boolean(string="Termination")
    termination_eosb = fields.Boolean(string="Termination Without EOSB")
