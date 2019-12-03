# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Sales Quotation / Order without Tax column on report",
    'summary': 'Quotation / Order without Tax column',
    'category': 'Sales',
    'author': 'Dyan Estacio',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'base', 'sale'
        ],
    'data': [
        'report/sales_qoutation.xml',
        
    ],
	'installable': True,
    'application': False,

}



