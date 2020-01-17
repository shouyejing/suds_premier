# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Products Published & Unpublished on website',
    'version' : '1.0',
    'category': 'eCommerce',
    'summary': 'Products Published & Unpublished on website',
    'description': """Products Published & Unpublished on website
""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'depends': ['website_sale'],
    'images': ['static/description/main_screen.jpg'],
    'data': [
        'wizard/view_published_unpublished.xml',
        ],
    'price': 10.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}