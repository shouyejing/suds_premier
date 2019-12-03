from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class PurchaseAnalytic(models.Model):
    _inherit='purchase.order'

    account_analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    branch_id = fields.Many2one('branches.cost.center', string="Branch", related='account_analytic_id.branch_id')
    company_name = fields.Char(related="company_id.name", string="Company")
    
    @api.multi
    def submit_po(self):
        return self.write({'state': 'to approve'})

class PurchaseAnalyticOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    branch_id = fields.Many2one('branches.cost.center', string="Branch", related='account_analytic_id.branch_id')
    company_name = fields.Char(related="company_id.name", string="Company")


# class PurchaseRFQState(models.TransientModel):
#     _inherit = 'mail.compose.message'

#     @api.multi
#     def mail_purchase_order_on_send(self):
#         if self._context.get('purchase_mark_rfq_sent'):
#             order = self.env['purchase.order'].browse(self._context['default_res_id'])
#             if order.state == 'draft':
#                 order.state = 'draft'