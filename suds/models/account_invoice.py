from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    account_analytic_id = fields.Many2one('account.analytic.account',
        string='Analytic Account',
        related = 'invoice_id.analytic_account_id',
        store=True
        )