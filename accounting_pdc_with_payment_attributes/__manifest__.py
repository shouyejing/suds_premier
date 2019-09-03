# -*- coding: utf-8 -*-
{
    'name': "Accounting Post Dated Cheques(PDC) with Additional Attributes",
    'summary': """Integration of PDC and Payment Attributes""",
    'description': """
        Accounting module for integration of PDC and Payment Attributes:
            - Similar fields are reduced to clearer ones.
            - PDC reporting is retained and unchanged.
    """,
    'author': "Earvin Clyde Gatdula - Agilis Enterprise Solutions, Inc.",
    'website': "http://www.agilis-solutions.com/",
    'category': 'Accounting',
    'version': '0.1',

    'depends': [
        'contacts',
        'account_accountant',
        'sale_management',
        'accounting_payment_attributes',
        'account_check_printing'
        ],

    'data': [
        'views/accounting_pdc_payment_attributes.xml',
        'data/accounting_pdc_payment_attributes_data.xml',
    ],

    'demo': [

    ],
    "application": False,
    "installable": True,
}
