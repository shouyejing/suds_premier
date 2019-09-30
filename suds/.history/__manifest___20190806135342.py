# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Customization for SUDS Laundry & Dry Clean Services",
    'summary': 'Customization for SUDS',
    'category': 'Project',
    'author': 'Dyan Estacio',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'base', 'project', 'analytic', 'purchase', 'sale'
        ],
    'data': [
        
        'views/analytic_account.xml',
        'views/sales.xml',
        'views/sales_invoice.xml',
        'views/purchase.xml',
        'views/stock_picking.xml',
        'views/franchisee_profile_project.xml',
        'views/royalty_fee.xml',
        'report/sales_qoutation.xml',
        'report/sales_invoice.xml',
        'data/months.xml',
        'data/royalty_fee_reference.xml',
        'data/res.company.csv'
        
    ],
	'installable': True,
    'application': 

}



