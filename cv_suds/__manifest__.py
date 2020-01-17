# -*- coding: utf-8 -*-
{
    'name': "Check Voucher: SUDS",

    'summary': """
        Transforming Physical Check Voucher Forms into Electronic for SUDS""",

    'description': """
        This module's purpose is to make an electronic Check Voucher to be used by SUDS as part 
        of the company's transition into using Odoo ERP
    """,

    'author': "John Christian Ardosa(Agilis Enterprise Solutions)",
    'website': "http://agilis.com.ph",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'check_voucher_default'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/check_voucher_view.xml',
        # 'views/account_views_inherit.xml',
        'reports/report.xml',
        'reports/check_voucher.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}