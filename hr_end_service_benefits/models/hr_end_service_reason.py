from odoo import models, fields

class HrEndServiceReason(models.Model):
    _name = 'hr.end.service.reason'
    _description = 'Reason for Ending Service'

    name = fields.Char(string="Reason", required=True)
    deserved_after = fields.Float(string="Deserved After", required=True)
    zero_message = fields.Char(string="Zero Message")
    is_partial = fields.Boolean(string="Is Partial", required=True)
    line_ids = fields.One2many('hr.end.service.reason.line', 'reason_id', string="Reason Line")

class HrEndServiceReasonLine(models.Model):
    _name = 'hr.end.service.reason.line'
    _description = 'Reason Line for Ending Service'

    name = fields.Char(string="Sequence", required=True)
    reason_id = fields.Many2one('hr.end.service.reason', string="Reason", required=True)
    deserved_for_first = fields.Float(string="Deserved for First[Years]", required=True)
    deserved_month_for_year = fields.Float(string="Deserved Month for Year", required=True)
