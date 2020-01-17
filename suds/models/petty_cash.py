# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime as date
from odoo.exceptions import ValidationError, UserError, Warning
import logging
import itertools
import calendar
_logger = logging.getLogger("_name_")


class PettyCash(models.Model):
    _inherit = ['petty.cash']

    @api.multi
    def _get_date_time(self):
        return date.now()

    reason = fields.Char(string='Reason for Petty Cash')
    requested_by_date = fields.Datetime(string="Requested By Date", default=_get_date_time,
                                        readonly=True
                                        )
    lines_paid = fields.Boolean(string="All Lines Paid", compute='_lines_paid')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Requested'),
        ('cash_dispatch', 'Cash Dispatched'),
        ('to_reconcile', 'To Reconcile'),
        ('reconcile', 'Reconciled'),
        ('reject', 'Rejected'),
    ], string='Status', readonly=True, default='draft')

    @api.depends('petty_cash_line_ids.state')
    def _lines_paid(self):
        paid_lines = []
        for rec in self:
            petty_cash_line = rec.petty_cash_line_ids
            for i in petty_cash_line:
                paid_lines.append(str(i.state))
        if ('draft' not in paid_lines):
            self.lines_paid = True

    @api.multi
    def reject_request(self):
        self.write({
            'state': 'reject',
            'requested_by_date': date.now(),
        })
        return True


class PettyCashLine(models.Model):
    _inherit = 'petty.cash.line'

    account_expense_id = fields.Many2one(
        'account.account', 
        string='Account Expense',
        domain="[]",
        required=True
    )

    @api.multi
    def do_pay(self):
        res = super(PettyCashLine, self).do_pay()
        total = 0.0
        for line in self:
            line.state = 'draft'
            amount_received = line.cash_id.amount_received
            for rec in line.cash_id:
                petty_cash_line = rec.petty_cash_line_ids
                for record in petty_cash_line:
                    _logger.info(
                        '\n\n\n line state: {}'.format(str(record.state)))
                    if record.state == 'draft':
                        total += record.amount
            petty_balance = line.cash_id.petty_cash_balance + total
            round(petty_balance)
            _logger.info('\n\n\namount_received: {}\ntotal cash: {}\npetty cash balance: {}\n\n\n'.format(
                str(amount_received), str(total), str(petty_balance)))

            if line.cash_id.paid_amount_total > line.cash_id.amount_received:
                raise UserError(
                    _('You Can Not Pay More Then  Received Amount !'))
            elif line.amount > petty_balance:
                raise UserError(
                    _('You Can Not Pay More Than The Petty Cash Balance !'))
            else:
                line.state = 'paid'
                return res
