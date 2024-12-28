from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    eos_id = fields.Many2one('hr.end.service', string="End of Service")

