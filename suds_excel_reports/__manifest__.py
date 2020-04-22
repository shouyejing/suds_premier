# -*- coding: utf-8 -*-
{
    'name': "SUDS Excel Reports",

    'summary': """
        Prints Excel Files of SUDS' sales and purchase history reports,
        Print Sales and Invoice Report,
        Receivable Report,
        Payable Report""",

    'description': """
        Prints Excel Files of SUDS' sales and purchase history reports. Users
        can print 1 document or a selection of documents in the Sales and Purchase Tree View
    """,

    'author': "John Christian Ardosa, Ralf Cabarogias - Agilis Group",
    'website': "http://agilis.com.ph",

    'category': 'Reports',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/sales_invoice_report.xml',
        'reports/receivable_report.xml',
        'reports/payable_report.xml'
        # 'reports/excel_report_wizard.xml',
    ]
}
