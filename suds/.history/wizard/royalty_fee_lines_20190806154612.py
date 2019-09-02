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
            'line_id': line.id,
            'request_id': line.request_id.id,
            'product_id': line.product_id.id,
            'name': line.name or line.product_id.name,
            'product_qty': line.product_qty,
            'product_uom_id': line.product_uom_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super(RoyaltyFeetoInvoice, self).default_get(fields)
        request_line_obj = self.env['monthly.royalty.fees.line']
        request_line_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if not request_line_ids:
            return res
        assert active_model == 'monthly.royalty.fees.line', \
            'Bad context propagation'

        items = []
        for line in request_line_obj.browse(request_line_ids):
            items.append([0, 0, self._prepare_item(line)])
        
        res.update({'royalty_fee_to_invoice_ids':[(6,0,items)]})
        return res

class RoyaltyFeeLinestoInvoice(models.TransientModel):
    _name = 'royalty.fee.lines.to.invoice'

    royalty_fee_lines_id = fields.Many2one('royalty.fee.to.invoice')
    month_id = fields.Many2one('royalty.fee.month', string="Month")
    royalty_fee = fields.Float(string="Royalty Fee")



