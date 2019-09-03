from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class RoyaltyFeetoInvoice(models.TransientModel):
    _name='royalty.fee.to.invoice'

    royalty_fee_to_invoice_ids = fields.One2many('royalty.fee.lines.to.invoice','royalty_fee_lines_id', string="Royalty Fee to Invoice")
    is_royalty_fee = fields.Boolean(default=True)
    branch_id = fields.Many2one('branches.cost.center', string="Branch")

    @api.model
    def _prepare_item(self, line):
        return {
            'month': line.month,
            'royalty_fee': line.royalty_fee,
        }

    @api.model
    def default_get(self, fields):
        res = super(RoyaltyFeetoInvoice, self).default_get(fields)
        royalty_fee_line_obj = self.env['monthly.royalty.fees.line'].browse(self._context.get('active_id'))

        items = []
        for line in royalty_fee_line_obj:
            items.append([0, 0, self._prepare_item(line)])
        
        res.update({'royalty_fee_to_invoice_ids':[(6,0,items)]})
        return res

class RoyaltyFeeLinestoInvoice(models.TransientModel):
    _name = 'royalty.fee.lines.to.invoice'

    royalty_fee_lines_id = fields.Many2one('royalty.fee.to.invoice')
    month = fields.Many2one('royalty.fee.month', string="Month")
    royalty_fee = fields.Float(string="Royalty Fee")



