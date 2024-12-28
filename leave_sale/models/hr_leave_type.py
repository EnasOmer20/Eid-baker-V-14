from odoo import models, fields

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_annual_leave = fields.Boolean(
        string="Is Annual Leave",
        help="Mark this leave type as Annual Leave. Only these leave types will be considered when computing remaining leaves."
    )
