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

    

class RoyaltyFeeLinestoInvoice(models.TransientModel):
    _name = 'royalty.fee.lines.to.invoice'

    royalty_fee_lines_id = fields.Many2one('royalty.fee.to.invoice')
    month = fields.Many2one('royalty.fee.month', string="Month")
    royalty_fee = fields.Float(string="Royalty Fee")



