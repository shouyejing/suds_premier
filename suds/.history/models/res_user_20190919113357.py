from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class AllowedAnalyticAccountUser(models.Model):
    _inherit='res.users'

    allowed_analytic_accounts = fields.Many2many('account.analytic.account', string="Allowed Analytic Accounts")
    