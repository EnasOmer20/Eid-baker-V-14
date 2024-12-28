from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class LeaveSale(models.Model):
    _name = 'leave.sale'
    _description = 'Leave Sale Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Request Name", required=True, default="New", copy=False, readonly=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        tracking=True,
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
    )
    annual_leave_days = fields.Float(
        string="Annual Leave Days",
        related='employee_id.remaining_leaves',
        readonly=True
    )
    days_to_sell = fields.Float(string="Days to Sell", required=True)
    sale_amount = fields.Float(string="Sale Amount", compute="_compute_sale_amount", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', string="State", tracking=True)
    approver_id = fields.Many2one('res.users', string="Approver", required=False)
    move_id = fields.Many2one('account.move', string="Receipt", readonly=True, copy=False)
    receipt_count = fields.Integer('Receipt Count', compute='_compute_receipt_count')

    def _compute_receipt_count(self):
        for rec in self:
            rec.receipt_count = self.env['account.move'].search_count([('sale_leave_id', '=', rec.id)])

    @api.depends('days_to_sell')
    def _compute_sale_amount(self):
        for rec in self:
            working_days_per_month = rec.employee_id.contract_id.working_days_per_month
            rec.sale_amount = rec.days_to_sell * rec.employee_id.contract_id.wage / working_days_per_month if working_days_per_month > 0 else 1  # Example calculation

    def action_submit(self):
        for rec in self:
            rec.state = 'submitted'
            rec.message_post(body="Leave sale request submitted.")

    def action_approve(self):
        for rec in self:
            if rec.days_to_sell <= 0:
                raise UserError(_("Days to Sell must be greater than 0."))
            if rec.sale_amount <= 0:
                raise UserError(_("Sale Amount must be calculated and greater than 0."))

            # Check if the employee has enough remaining leaves
            if rec.days_to_sell > rec.annual_leave_days:
                raise UserError(_("You cannot sell more days than your remaining annual leave."))

            # Get the annual leave type
            annual_leave = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)], limit=1)

            allocations = self.env['hr.leave.allocation'].with_context(active_test=False).search([
                ('employee_id', '=', rec.employee_id.id),
                ('holiday_status_id', '=', annual_leave.id),
                ('state', '=', 'validate'),
            ]).filtered(lambda al: not al.employee_id.active)

            for allocation in allocations:
                allocation.number_of_days -= rec.days_to_sell
            # Deduct the days sold from the employee's annual leave days
            rec.employee_id.remaining_leaves -= rec.days_to_sell

            # Create a receipt for the employee
            self._create_receipt()

            rec.state = 'approved'
            rec.message_post(body="Leave sale request approved, days deducted, and receipt created.")

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec.message_post(body="Leave sale request rejected.")

    def _create_receipt(self):
        """Method to create an account.move receipt for the employee."""
        for rec in self:
            partner_id = rec.employee_id.address_home_id.id
            if not partner_id:
                raise UserError(_("The employee does not have a home address set to generate the receipt."))

            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            if not journal:
                raise UserError(_("Please configure a sales journal to create the receipt."))


            move_vals = {
                'move_type': 'out_receipt',  # Use 'out_receipt' for a 	Sales Receipt
                'partner_id': partner_id,
                'journal_id': journal.id,
                'invoice_date': fields.Date.today(),
                'sale_leave_id': rec.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'name': _("Leave Sale for %s") % rec.name,
                        'quantity': 1,
                        'price_unit': rec.sale_amount,
                        'account_id': journal.default_account_id.id,
                    })
                ],
            }

            move = self.env['account.move'].create(move_vals)
            # move.action_post()  # Post the journal entry
            rec.move_id = move.id
            rec.message_post(body=_("Receipt of %s created for employee.") % rec.sale_amount)

    def action_view_receipt(self):
        return {
            'name': 'Receipts',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('sale_leave_id', '=', self.id)],
        }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('leave.sale') or 'New'
        return super(LeaveSale, self).create(vals)

    @api.constrains('days_to_sell')
    def _check_days_to_sell(self):
        for rec in self:
            if rec.days_to_sell > rec.annual_leave_days:
                raise ValidationError(_("Days to Sell cannot be greater than Annual Leave Days."))

