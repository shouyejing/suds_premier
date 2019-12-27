# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime as date
from odoo.exceptions import ValidationError, UserError, Warning


class PettyCash(models.Model):
    _inherit = ['petty.cash']

    @api.multi
    def _get_date_time(self):
        return date.now()

    reason = fields.Char(string='Reason for Petty Cash')
    requested_by_date = fields.Datetime(string="Requested By Date", default=_get_date_time,
                                        readonly=True
                                        )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Requested'),
        ('cash_dispatch', 'Cash Dispatched'),
        ('to_reconcile', 'To Reconcile'),
        ('reconcile', 'Reconciled'),
        ('reject', 'Rejected'),
    ], string='Status', readonly=True, default='draft')

    @api.multi
    def reject_request(self):
        self.write({
            'state': 'reject',
            'requested_by_date': date.now(),
        })
        return True
