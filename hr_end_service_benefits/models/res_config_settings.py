from odoo import models, fields

class HrEndServiceSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expense_account_id = fields.Many2one('account.account', string="Default Expense Account")
    payment_journal_id = fields.Many2one('account.journal', string="Default Payment Journal")
    expense_journal_id = fields.Many2one('account.journal', string="Default Expense Journal")

    def set_values(self):
        super(HrEndServiceSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('hr_end_service.expense_account_id', self.expense_account_id.id)
        self.env['ir.config_parameter'].set_param('hr_end_service.payment_journal_id', self.payment_journal_id.id)
        self.env['ir.config_parameter'].set_param('hr_end_service.expense_journal_id', self.expense_journal_id.id)

    def get_values(self):
        res = super(HrEndServiceSettings, self).get_values()
        res.update({
            'expense_account_id': self.env['ir.config_parameter'].get_param('hr_end_service.expense_account_id'),
            'payment_journal_id': self.env['ir.config_parameter'].get_param('hr_end_service.payment_journal_id'),
            'expense_journal_id': self.env['ir.config_parameter'].get_param('hr_end_service.expense_journal_id'),
        })
        return res