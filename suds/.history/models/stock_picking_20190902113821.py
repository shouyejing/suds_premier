from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class DeliveryAnalyticAccount(models.Model):
    _inherit='stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    
    company_name = fields.Char(related="company_id.name", string="Company")

    # @api.depends('origin')
    # def _get_analytic_account(self):
    #     for i in self:
    #         stock_source = self.env['sale.order'].search([('name', '=', i.origin)], limit=1)

    #         if stock_source:
    #             i.account_analytic_id = stock_source.analytic_account_id
            
    #         else:
    #             stock_source = self.env['purchase.order'].search([('name', '=', i.origin)], limit=1)
    #             i.account_analytic_id = stock_source.account_analytic_id



