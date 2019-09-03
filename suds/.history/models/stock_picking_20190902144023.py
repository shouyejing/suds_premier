from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class DeliveryAnalyticAccount(models.Model):
    _inherit='stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", compute="_get_analytic_account")
    
    company_name = fields.Char(related="company_id.name", string="Company")

    @api.depends('origin')
    def _get_analytic_account(self):
        for i in self:
            stock_source_outgoing = self.env['sale.order'].search([('name', '=', i.origin)], limit=1)
            stock_source_incoming = self.env['purchase.order'].search([('name', '=', i.origin)], limit=1)
            if i.picking_type_code =='incoming':
                i.account_analytic_id = stock_source_incoming.account_analytic_id.id
            
            elif i.picking_type_code == 'outgoing':
                i.account_analytic_id = stock_source_outgoing.account_analytic_id

            else:
                i.account_analytic_id = ""



