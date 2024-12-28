from odoo import models, fields, api, _
from odoo.exceptions import UserError

def number_to_ordinal(n):
    """Helper function to convert a number to its ordinal string."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

class HRPenalSanction(models.Model):
    _name = 'hr.penal.sanction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Penal Sanctions'

    # Main Fields
    name = fields.Char(string="Sanction Name", required=True, default="New", copy=False, readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    category_id = fields.Many2one('hr.penal.category', string="Category")
    violation_id = fields.Many2one('hr.penal.violation', string="Violation",domain="[('category_id', '=', category_id)]", required=True)
    stage_id = fields.Many2one('hr.penal.stage', string="Stage", domain="[('category_id', '=', category_id)]" , required=True)
    instance_count = fields.Char(string="Instance of Violation", compute="_compute_instance_count", store=True)
    is_salary_deduction = fields.Boolean(string="Salary Deduction", related='stage_id.salary_deduction', store=True)
    amount = fields.Float(string="Amount", digits=(16, 2))
    date = fields.Date(string="Date", default=fields.Date.context_today)
    notes = fields.Text(string="Notes")

    # Approval Fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('hr_confirmed', 'HR Confirmed')
    ], string='Status', default='draft', readonly=True, tracking=True)

    first_approver_id = fields.Many2one('res.users', string="Direct Manager", compute="_compute_direct_manager", store=True)
    second_approver_id = fields.Many2one('res.users', string="Department Manager", compute="_compute_department_manager", store=True)
    hr_manager_id = fields.Many2one('res.users', string="HR Manager", compute="_compute_hr_manager", store=True)

    @api.depends('employee_id', 'violation_id')
    def _compute_instance_count(self):
        for record in self:
            if record.employee_id and record.violation_id:
                # Count previous violations for this employee and violation
                count = self.env['hr.penal.sanction'].search_count([
                    ('employee_id', '=', record.employee_id.id),
                    ('violation_id', '=', record.violation_id.id)
                ])
                # Convert count + 1 to ordinal string
                record.instance_count = number_to_ordinal(count + 1)
            else:
                record.instance_count = number_to_ordinal(1)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.penal.sanction') or 'New'
        return super(HRPenalSanction, self).create(vals)

    @api.depends('employee_id')
    def _compute_direct_manager(self):
        for record in self:
            record.first_approver_id = record.employee_id.parent_id.user_id

    @api.depends('employee_id')
    def _compute_department_manager(self):
        for record in self:
            department_manager = record.employee_id.department_id.manager_id.user_id
            record.second_approver_id = department_manager

    @api.depends('employee_id')
    def _compute_hr_manager(self):
        hr_manager = self.env['hr.department'].search([('is_hr_department', '=', True)], limit=1).manager_id.user_id
        for record in self:
            record.hr_manager_id = hr_manager

    # Button Actions
    def action_first_approval(self):
        if self.env.user != self.first_approver_id:
            raise UserError(_("Only the Direct Manager can approve this record."))
        self.write({'state': 'first_approval'})

    def action_second_approval(self):
        if self.env.user != self.second_approver_id:
            raise UserError(_("Only the Department Manager can approve this record."))
        self.write({'state': 'second_approval'})

    def action_hr_confirm(self):
        if self.env.user != self.hr_manager_id:
            raise UserError(_("Only the HR Manager can confirm this record."))
        self.write({'state': 'hr_confirmed'})

        # Trigger Email Notification
        template = self.env.ref('hr_penalty_sanction.hr_penalty_notification_email_template')
        if template:
            template.send_mail(self.id, force_send=True)
