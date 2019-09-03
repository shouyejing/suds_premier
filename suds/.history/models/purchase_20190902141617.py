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

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        #override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        #choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
            result['analytic_account_id'] = self.account_analytic_id.id
            _logger.info("/n/n/n/n result %s /n/n/n/n" % (str(result['analytic_account_id'])))
        return result

class PurchaseAnalyticOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    branch_id = fields.Many2one('branches.cost.center', string="Branch", related='account_analytic_id.branch_id')
    company_name = fields.Char(related="company_id.name", string="Company")