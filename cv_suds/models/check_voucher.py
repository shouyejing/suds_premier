# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import logging
import itertools
import calendar
from odoo.exceptions import ValidationError
from num2words import num2words
_logger = logging.getLogger("_name_")

class CheckVoucher(models.Model):
    _description = 'Model used for creating Check Vouchers'
    _rec_name = 'voucher_id_seq'
    _inherit = 'check.voucher'

    STATUS = [
        ('draft', 'Draft'),
        ('certified', 'Certified'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    state = fields.Selection(STATUS, string="Status",
                             default="draft", readonly=True, copy=False)

    # ===============================================================
    """States and related fields and methods"""
    # ===============================================================

    prepared_by_id = fields.Many2one(
        'res.users', string="Prepared By: ", ondelete='cascade',
        readonly=True
    )

    date_certified = fields.Datetime(
        string='Date Certified',
        readonly=True

    )
    certified_correct_by_id = fields.Many2one(
        'res.users', string="Certified Correct By: ", ondelete='cascade',
        readonly=True
    )

    date_approved = fields.Datetime(
        string='Date Approved',
        readonly=True
    )
    approved_by_id = fields.Many2one(
        'res.users', string="Approved By: ", ondelete='cascade',
        readonly=True
    )

    date_rejected = fields.Datetime(
        string='Date Rejected',
        readonly=True
    )
    
    rejected_by_id = fields.Many2one(
        'res.users', string="Rejected By: ", ondelete='cascade',
        readonly=True 
    )

    @api.multi
    def certify_voucher(self):
        debit_total = 0
        credit_total = 0
        for i in self:
            for j in i.account_ids:
                debit_total += round(j.debit_amount,2)
                credit_total += round(j.credit_amount,2)
                _logger.info("\n\n\nDebit Amount: %s\nCredit Amount: %s \n\n\n\n"%(str(debit_total),str(credit_total)))
        if debit_total != credit_total:
            raise ValidationError(
                _("Total Debit Amount must be the same as Total Credit Amount"))
        elif debit_total != i.payment_id.amount and credit_total != i.payment_id.amount:
            raise ValidationError(
                _("Total Debit Amount and Credit Amount must be the same as Payment Amount"))
        elif self.total_amount != self.payment_id.amount:
            raise ValidationError(
                _('Total Amount must be exactly the same as Payment Amount'))
        else:
            self.write({
                'state': 'certified',
                'date_certified': datetime.now(),
                'certified_correct_by_id': self._uid,
            })
        return True

    @api.multi
    def approve_voucher(self):
        self.write({
            'state': 'approved',
            'date_approved': datetime.now(),
            'approved_by_id': self._uid,
        })
        return True

    @api.multi
    def reject_voucher(self):
        self.write({
            'state': 'rejected',
            'date_rejected': datetime.now(),
            'rejected_by_id': self._uid,
        })
        return True

    @api.multi
    def reset_to_draft(self):
        self.write({
            'state': 'draft',
            'date_certified': False,
            'date_approved': False,
            'date_rejected': False,
            'certified_correct_by_id': False,
            'approved_by_id': False,
            'rejected_by_id': False,
        })


    @api.onchange('invoice_ids', 'invoice_ids.amount')
    def _get_total_amount(self):
        for i in self:
            total = 0
            for rec in i.invoice_ids:
                total += rec.amount
            i.total_amount = total

    @api.onchange('total_amount', 'currency_id')
    def _onchange_amount(self):
        if self.currency_id:
            self.amount_in_words = self.currency_id.amount_to_text(
                self.total_amount)

    # Overriding the create method to add sequencing to Iteration ID
    @api.model
    def create(self, vals):
        if vals.get('voucher_id_seq', _('New')) == ('New'):
            vals['voucher_id_seq'] = self.env['ir.sequence'].next_by_code(
                'voucher.number.sequence') or _('New')
            vals['prepared_by_id'] = self._uid
        result = super(CheckVoucher, self).create(vals)
        self.env['account.payment'].browse(vals.get('payment_id')).write({
            'check_voucher_id': result.id})
        return result


class Particulars(models.Model):
    _inherit = 'check.voucher.particulars'

# class AccountPayment(models.Model):
#     _inherit = 'account.payment'

# # ==========Cheque Details==========
#     cheque_ref = fields.Char(string="Cheque Reference")
#     cheque_date = fields.Date(string="Cheque Date")
#     bank_ref_id = fields.Many2one('res.partner.bank', string="Bank Reference")
#     # bank_id = fields.Many2one('account.journal',
#     #                           string="Bank Reference",
#     #                           domain=[('type', 'in', ['bank'])])
#     cheque_date_rcv = fields.Date(string="Cheque Date Received")
#     cheque_date_cleared = fields.Date(string="Cheque Date Cleared")

# # ==========Receipt Details==========
#     probationary_receipt_no = fields.Char(string="Probationary Receipt Number")
#     ack_receipt_no = fields.Char(string="Acknowledgement Receipt Number")
#     official_receipt_no = fields.Char(string="Official Receipt Number")

# class PartnerBank(models.Model):
#     _inherit = 'res.partner.bank'

#     @api.multi
#     def name_get(self):
#         data = []
#         for i in self:
#             display_value = '{} - {}'.format(i.bank_id.name, i.acc_number)
#             data.append((i.id, display_value))
#         return data

class AccountDistribution(models.Model):
    _inherit = "check.voucher.account_distribution"

