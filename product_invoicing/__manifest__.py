# -*- coding: utf-8 -*-
{
    'name': "Product Ordered/Delivered Invoicing Setter",

    'summary': """
        Provides a way to select multiple products and set their invoicing either ordered or delivered""",

    'description': """
        Long description of module's purpose
    """,

    'author': "John Christian Ardosa",
    'website': "http://www.agilis.com.ph",
    'category': 'Product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        'wizard/product_ordered_delivered_wizard.xml',
    ],
}