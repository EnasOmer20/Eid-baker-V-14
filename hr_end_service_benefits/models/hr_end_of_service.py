from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class HREndServiceRequest(models.Model):
    _name = 'hr.end.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'End of Service Request'

    name = fields.Char(string="Request Name", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    hiring_date = fields.Date(related='employee_id.hiring_date', string="Hiring Date", store=True)
    service_date_years = fields.Float(string="Service Date [Years]",compute="_compute_service_date_in_years", store=True)
    years = fields.Float(string="Years", compute="_compute_service_date_in_years")
    months = fields.Float(string="Months", compute="_compute_service_date_in_years")
    days = fields.Float(string="Days", compute="_compute_service_date_in_years")
    reword_type = fields.Selection([('replacement', 'Replacement'), ('ending_service', 'Ending Service')], string="Reword Type", required=True)
    reason_id = fields.Many2one('hr.end.service.reason', string="Reason", required=True)
    date_request = fields.Date(string="Request Date", default=fields.Date.today)
    date_approval = fields.Date(string="Approval Date")
    date_payment = fields.Date(string="Payment Date")
    unpaid_leave_days = fields.Float('Unpaid Leave Days', compute='_compute_service_date_in_years', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr_approval', 'HR Approval'),
        ('accounting', 'Accounting'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)
    total_deserved_amount = fields.Float(string="Total Deserved Amount", compute="_compute_total_amount", store=True)
    requested_amount = fields.Float(string="Requested Amount")
    previously_disbursed_amount = fields.Float(string="Previously Disbursed Amount", compute="_compute_disbursed_amount", store=True)
    available_amount = fields.Float(string="Available Amount", compute="_compute_available_amount", store=True)
    is_partial = fields.Boolean(related='reason_id.is_partial', string="partial", default=False)
    notes = fields.Text(string="Notes")
    move_id = fields.Many2one('account.move', string="Receipt", readonly=True, copy=False)
    receipt_count = fields.Integer('Receipt Count', compute='_compute_receipt_count')

    def _compute_receipt_count(self):
        for rec in self:
            rec.receipt_count = self.env['account.move'].search_count([('eos_id', '=', rec.id)])

    @api.constrains('requested_amount')
    def _check_requested_amount(self):
        for record in self:
            if record.requested_amount < 0.0:
                raise UserError(_("Requested amount cannot be negative"))
            if record.requested_amount > record.available_amount:
                raise UserError(_("Requested amount cannot be greater than available amount"))

    @api.onchange('reason_id')
    def get_requested_amount(self):
        if not self.is_partial:
            self.requested_amount = self.available_amount

    @api.depends('employee_id','reason_id')
    def _compute_disbursed_amount(self):
        for record in self:
            record.previously_disbursed_amount = 0.0
            if record.reason_id and record.employee_id:
                record.previously_disbursed_amount = self.search([('employee_id', '=', record.employee_id.id),('reason_id', '=', record.reason_id.id),('state', '=', 'done')], limit=1).requested_amount

    @api.depends('total_deserved_amount', 'previously_disbursed_amount')
    def _compute_available_amount(self):
        for record in self:
            record.available_amount = record.total_deserved_amount - record.previously_disbursed_amount

    @api.depends('reason_id', 'reason_id.line_ids', 'employee_id.contract_id.wage',
                 'service_date_years', 'unpaid_leave_days')
    def _compute_total_amount(self):
        for record in self:
            total_amount = 0.0
            if record.reason_id and record.employee_id:
                # Retrieve employee contract details
                contract = record.employee_id.contract_id
                wage = contract.wage or 0.0
                hra = contract.hra or 0.0
                da = contract.da or 0.0
                travel_allowance = contract.travel_allowance or 0.0
                meal_allowance = contract.meal_allowance or 0.0
                medical_allowance = contract.medical_allowance or 0.0
                other_allowance = contract.other_allowance or 0.0
                working_days_per_month = contract.working_days_per_month or 1.0

                # Total monthly income including all allowances
                total_monthly_income = wage + hra + da + travel_allowance + \
                                       meal_allowance + medical_allowance + other_allowance

                service_years = record.service_date_years

                # Iterate through the benefit lines
                for line in record.reason_id.line_ids:
                    if service_years > 0:
                        # Determine the applicable years for the current rule
                        applicable_years = min(service_years, line.deserved_for_first)

                        # Calculate the benefit for these years
                        total_amount += applicable_years * line.deserved_month_for_year * total_monthly_income

                        # Reduce remaining service years
                        service_years -= applicable_years
                    else:
                        break  # Stop if no service years are left

                # daily_wage = total_monthly_income / working_days_per_month
                # unpaid_leave_amount = record.unpaid_leave_days * daily_wage
                # total_amount += unpaid_leave_amount

            # Assign the computed amount to the field
            record.total_deserved_amount = total_amount

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('end.of.service') or 'New'
        return super(HREndServiceRequest, self).create(vals)

    @api.depends('hiring_date')
    def _compute_service_date_in_years(self):
        for record in self:
            if record.hiring_date:
                today = fields.Date.today()
                difference = relativedelta(today, record.hiring_date)
                # Get the annual leave type
                annual_leave = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)], limit=1)

                allocations = self.env['hr.leave.allocation'].with_context(active_test=False).search([
                    ('employee_id', '=', record.employee_id.id),
                    ('holiday_status_id', '=', annual_leave.id),
                    ('state', '=', 'validate'),
                ]).filtered(lambda al:  not al.employee_id.active)
                number_of_days = 0
                for allocation in allocations:
                    number_of_days += allocation.number_of_days

                record.unpaid_leave_days = number_of_days
                # Calculate the total years including fractional years
                record.service_date_years = difference.years + (difference.months / 12.0)
                record.years = difference.years
                record.months = difference.months
                record.days = difference.days
            else:
                record.service_date_years = 0.0
                record.years = 0.0
                record.months = 0.0
                record.days = 0.0


    def action_submit(self):
        self.state = 'hr_approval'
        # Send email notification to HR Manager
        self.message_post(body=_("End of Service Request submitted for approval."))

    def action_approve_hr(self):
        self.state = 'accounting'
        # Notify accounting team
        self.message_post(body=_("HR Manager approved the request. Awaiting accounting processing."))

    def action_approve_accounting(self):
        #create receipt
        self._create_receipt()
        self.state = 'done'
        # Archive employee and cancel contract
        if not self.is_partial:
            self.employee_id.active = False
            self.employee_id.contract_id.state = 'cancel'
        self.message_post(body=_("Accounting approved the request. Process completed."))

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
                'eos_id': rec.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'name': _("End of Service benefit for %s") % rec.name,
                        'quantity': 1,
                        'price_unit': rec.requested_amount,
                        'account_id': journal.default_account_id.id,
                    })
                ],
            }

            move = self.env['account.move'].create(move_vals)
            # move.action_post()  # Post the journal entry
            rec.message_post(body=_("Receipt of %s created for employee.") % rec.requested_amount)

    def action_view_receipt(self):
        return {
            'name': 'Receipts',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('eos_id', '=', self.id)],
        }

