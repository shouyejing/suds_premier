# -*- coding: utf-8 -*-
{
    'name': "Product Attributes in Sales",
    'summary': """Adding attributes in products. Under Sales category""",
    'description': """
        Sales module for Adding attributes in Product:
            - Addition of Item Type, Generic/Branded products and relationships
            - Attributes in size such as length, width, and height
    """,
    'author': "Earvin Clyde Gatdula - Agilis Enterprise Solutions, Inc.",
    'website': "http://www.agilis-solutions.com/",
    'category': 'Sales',
    'version': '0.1',

    'depends': [
        'sale_management', 'account_invoicing', 'product_brand'
        ],

    'data': [
        'security/ir.model.access.csv',
        'views/product_attributes.xml',
        ],

    'demo': [

        ],
    "application": False,
    "installable": True,
}
