# -*- coding: utf-8 -*-
'''
Created on March 2020

@author: Jovi Raynel Sanchez
'''



from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger("_name_")

class inheritSales(models.Model):
    _inherit = 'sale.order'

    payment_status = fields.Char(string="Payment Status", compute="sales")

    @api.depends('invoice_count')
    def sales(self):
        for i in self:
            invoice = self.env['account.invoice'].search([('origin', '=', i.name)])
            _logger.info('\n\n\nValue %s\n\n\n'%(invoice))
            i.payment_status = dict(invoice._fields['state'].selection).get(invoice.state)


class inheritPurchase(models.Model):
    _inherit = 'purchase.order'

    payment_status = fields.Char(string="Payment Status", compute="purchase")

    @api.depends('invoice_count')
    def purchase(self):
        for i in self:
            invoice = self.env['account.invoice'].search([('origin', '=', i.name)])
            _logger.info('\n\n\nValue %s\n\n\n'%(invoice))
            i.payment_status = dict(invoice._fields['state'].selection).get(invoice.state)
