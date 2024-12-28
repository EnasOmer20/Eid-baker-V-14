from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    receipt_id = fields.Many2one('account.move', string="Receipt", readonly=True)  # New Field

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_validate(self):
        """Override to generate an out_receipt when batch is validated."""
        # Call the super to keep the original behavior
        super(HrPayslipRun, self).action_validate()

        account_move_obj = self.env['account.move']
        for payslip in self.slip_ids:
            # Ensure the company's partner is set
            company = payslip.company_id
            partner = company.partner_id
            if not partner:
                raise ValidationError("Company %s does not have a partner set." % company.name)

            # Get the salary net rule
            salary_net_rule = payslip.line_ids.filtered(lambda line: line.code == 'NET')
            if not salary_net_rule:
                raise ValidationError("No NET salary rule found for %s" % payslip.employee_id.name)

            net_amount = salary_net_rule.total
            salary_account = salary_net_rule.salary_rule_id.account_credit

            if not salary_account:
                raise ValidationError("No salary account set for the NET rule in %s" % payslip.employee_id.name)

            # Create the out_receipt
            move_vals = {
                'move_type': 'out_receipt',  # Set to out_receipt
                'partner_id': partner.id,  # Partner = Company
                'ref': 'Payslip Receipt - %s' % payslip.name,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    (0, 0, {
                        'name': 'Net Salary for %s' % payslip.name,
                        'quantity': 1,
                        'price_unit': net_amount,
                        'account_id': salary_account.id,
                    }),
                ],
            }
            move = account_move_obj.create(move_vals)
            payslip.write({'receipt_id': move.id})  # Link invoice to payslip
