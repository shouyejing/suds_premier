# -*- coding: utf-8 -*-
{
    'name': "SUDS Modules Installer",
    'summary': """Installs all modules related to SUDS Laundry & Dry Clean Services""",
    'description': """
        List of modules for SUDS:
            - Customization for SUDS Laundry & Dry Clean Services
            - Accounting Additional Payment Details
            - Accounting Post Dated Cheques(PDC) with Additional Attributes
            - Account Payment Voucher
            - Payment Voucher with Cost Centre Analytics
            - Petty Cash Management
            - Check Printing Base
            - Product Pack
    """,
    'author': "Dyan Estacio - Agilis Enterprise Solutions, Inc.",
    'website': "http://www.agilis-solutions.com/",
    'category': 'Tools',
    'version': '0.1',

    'depends': [
        'account_accountant',
        'contacts',
        'purchase',
        'sale_management',
        'stock',
        'account_check_printing',
        'accounting_payment_attributes',
        'accounting_pdc_with_payment_attributes',
        'account_pdc_payment_report',
        'product_brand',
        'product_attributes',
        'purchase_request',
        'wk_product_pak',
        'suds'
        ],

    'data': [
    ],

    'demo': [
    ],
    "application": False,
    "installable": True,
}
