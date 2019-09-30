# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Batch Confirm of Sales Qoutation",
    'summary': 'Mutiple confirmation of Sales Qoutation',
    'category': 'Sales',
    'author': 'Dyan Estacio',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'base','sales'
        ],
    'data': [
        'views/vendor_bills.xml'
        
    ],
	'installable': True,
    'application': False,

}
