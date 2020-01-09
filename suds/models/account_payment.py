# -*- encoding: utf-8 -*-

from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    journal_type = fields.Selection(
        string='journal_type',
        selection=[
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
        ],

        related='journal_id.type',
        readonly=True,
        store=True

    )

# ==========Cheque Details==========
    cheque_ref = fields.Char(string="Cheque Reference")
    cheque_date = fields.Date(string="Cheque Date")
    bank_ref_id = fields.Many2one('res.partner.bank', string="Bank Reference")
    bank_id = fields.Many2one('account.journal',
                              string="Bank Reference",
                              domain=[('type', 'in', ['bank'])])
    cheque_date_rcv = fields.Date(string="Cheque Date Received")
    cheque_date_cleared = fields.Date(string="Cheque Date Cleared")

# ==========Receipt Details==========
    probationary_receipt_no = fields.Char(string="Probationary Receipt Number")
    ack_receipt_no = fields.Char(string="Acknowledgement Receipt Number")
    official_receipt_no = fields.Char(string="Official Receipt Number")


class PartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.multi
    def name_get(self):
        data = []
        for i in self:
            display_value = '{} - {}'.format(i.bank_id.name, i.acc_number)
            data.append((i.id, display_value))
        return data
