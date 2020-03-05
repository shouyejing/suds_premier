# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo import SUPERUSER_ID


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    website_order_configuration = fields.Selection(
        [
            ('confirm', 'Confirm Quotation'),
            ('invoice', 'Confirm Quotation and Create Invoice'),
            ('validate', 'Confirm Quotation and Validate Invoice'),
            ('payment', 'Confirm Quotation, Validate Invoice and Create Payment')
        ],
        string="Website Order Configuration"
    )