# -*- coding: utf-8 -*-
{
    'name': "Suds L1/L2 Group Access",

    'summary': """
        Controls Access Rights and Restrictions for Groups L1 and L2""",

    'description': """
        This module adds user access to specific buttons in the following apps:
        1. Sales
        2. Account
        3. Purchase
        4. Inventory
        Groups L1 and L2 will be given access to the buttons in the aforementioned apps.
    """,

    'author': "John Christian Ardosa",
    'website': "http://www.agilis-solutions.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'User Groups',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'ks_dashboard_ninja', 'account_asset', 'sale','itm_petty_cash','stock','purchase','suds'],

    # always loaded
    'data': [
        'views/accounting_view.xml',
        'views/asset_management_view.xml',
        'views/tax_adjustment_view.xml',
        'views/lock_dates.xml',
        # 'views/menu_items.xml',
        'views/petty_cash_view.xml',
        'views/purchase_view.xml',
        'views/inventory_view.xml',
        'views/sales_view.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
