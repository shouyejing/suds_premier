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
    lines_paid = fields.Boolean(string="All Lines Paid",compute='_lines_paid')

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

    @api.multi
    def do_pay(self):
        res = super(PettyCashLine, self).do_pay()
        for line in self:
            cash = line.amount if line.state == 'draft' else 0
            petty_balance = line.cash_id.petty_cash_balance + cash
            round(petty_balance)
            _logger.info('\n\n\ntotal cash: {}\npetty cash balance: {}\n\n\n'.format(
                str(cash), str(petty_balance)))

            if line.cash_id.paid_amount_total > line.cash_id.amount_received:
                raise UserError(
                    _('You Can Not Pay More Then  Received Amount !'))
            elif cash > petty_balance:
                raise UserError(
                    _('You Can Not Pay More Than The Petty Cash Balance !'))
            else:
                return res
