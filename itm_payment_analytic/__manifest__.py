# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Payment Analytic.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

{
    'name': 'Payment Voucher with Cost Centre Analytics',
    'category': 'Account',
    'author': 'ITMusketeers Consultancy Services LLP',
    'website': 'www.itmusketeers.com',
    'description': """
================================================================================

1. Account Payment Analytic Management.

================================================================================
""",
    'depends': ['base', 'analytic', 'web', 'payment', 'account', 'account_invoicing', 'itm_payment'],
    'summary': 'Manage Payment Analytic Account .',
    'data': [
        'views/account_payment_view.xml'],
    'images':['static/description/Banner.png'],
    'price': '25.00',
    'currency': "EUR",
    'installable': True,
}
