from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ConfirmQuotation(models.TransientModel):
    _name='batch.confirm.sale.quotation'

    quotation_to_confirm = fields.One2many('quotation.to.confirm', 'quotation_id')


class QuotationToConfirm(models.TransientModel):
    _name='quotation.to.confirm'

    quotation_id = fields.Many2one('batch.confirm.sale.quotation')
    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner')
    amount_total = fields.Float(string="Total")