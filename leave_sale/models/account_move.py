# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    sale_leave_id = fields.Many2one('leave.sale',string="Leave Sale")
