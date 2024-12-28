# -*- coding: utf-8 -*-


from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    working_days_per_month = fields.Float('Working days/month', help='Using to calculate wage/day.',required=True)
    working_hours_per_day = fields.Float('Working hours/day' ,required=True)
    hra = fields.Monetary(string='HRA', help="House rent allowance.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    da = fields.Monetary(string="DA", help="Dearness allowance")
    meal_allowance = fields.Monetary(string="Meal Allowance", help="Meal allowance")
    medical_allowance = fields.Monetary(string="Medical Allowance", help="Medical allowance")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")
