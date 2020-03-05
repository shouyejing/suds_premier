# -*- coding: utf-8 -*-
{
    'name': "Website Backend Auto Operation",

    'summary': """
         This module attempts to alter the behaviour of 
                    the original Website Backend Auto Operation
                    where all website order configurations can be 
                    used on all active payment acquirers or a 
                    select few.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "John Christian Ardosa",
    'website': "http://www.agilis.com.ph",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_backend_auto_operation'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/config.xml',
    ]
}