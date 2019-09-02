# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Invoice Source Document',
    'summary': 'Invoice Source Document',
    'category': 'Invoice',
    'author': 'Dyan Estacio',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        
        'sale_management',
        'account'
        ],
    'data': [
        'views/invoice_source.xml'
    ],
	'installable': True,
    'application': False,

}
