# -*- coding: utf-8 -*-
{
    'name': "P&J Modules Installer",
    'summary': """Installs all modules related to P&J Agricultural Trading""",
    'description': """
        List of modules for P&J:
            - Accounting and Finance
            - Sales Management
            - Purchase Management
            - Inventory Management
            - Employee Directory
            - Contacts Directory
            - Check Printing Base
            - Accounting Post Dated Cheques(PDC) with Additional Attributes
            - PDC Payments Report
            - Accounting Credit Limit
            - Accounting Additional Payment Attributes
            - Levels of Approval in Sales
            - Adjusted Use of Promotion Program
            - Company Profile
            - Product Brand Manager
            - Product Attributes in Sales
            - Request Purchase Product
            - Stock Delivery Details
            - Classification:In-house/Outsourced for Salespersonnel
            - Minimum And Maximum Price Of Product
    """,
    'author': "Earvin Clyde Gatdula - Agilis Enterprise Solutions, Inc.",
    'website': "http://www.agilis-solutions.com/",
    'category': 'Tools',
    'version': '0.1',

    'depends': [
        'account_accountant',
        'contacts',
        'hr',
        'purchase',
        'sale_management',
        'stock',
        'account_check_printing',
        'accounting_credit_limit',
        'accounting_payment_attributes',
        'accounting_pdc_with_payment_attributes',
        'account_pdc_payment_report', #should be the modified module('account_pdc' OMITTED in depends)
        'hr_company_profile',
        'product_brand',
        'product_attributes',
        'purchase_request',
        'stock_delivery_details',
        'sale_confirm_levels',
        'sale_inhouse_outsource_agent',
        'sale_promotion_free_products',
        'sh_min_max_price',
        'p&j_product_attributes',
        'p&j_sales_levels_credit_limit',
        'pj_purchasing_classifications',
        ],

    'data': [
    ],

    'demo': [
    ],
    "application": False,
    "installable": True,
}
