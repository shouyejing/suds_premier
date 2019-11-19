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
        'base', 'project', 'analytic', 'ks_dashboard_ninja', 'purchase', 'purchase_request', 'sale', 'purchase_requisition', 'website_quote', 'account', 'account_accountant', 'itm_petty_cash'
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/royalty_fee_lines.xml',
        'wizard/sale_to_project.xml',
        'views/analytic_account.xml',
        'views/sales.xml',
        'views/sales_invoice.xml',
        'views/purchase.xml',
        'views/stock_picking.xml',
        'views/project.xml',
        'views/royalty_fee.xml',
        'views/customer.xml',
        'views/res_user.xml',
        'views/petty_cash_view_inherit.xml',
        'views/quote_template.xml',
        'report/sales_qoutation.xml',
        'report/sales_invoice_without_payment.xml',
        'report/picking_operations.xml',
        'report/delivery_receipt.xml',
        'report/service_invoice.xml',
        'report/invoice_multiple_so.xml',
        'data/months.xml',
        'data/royalty_fee_reference.xml',
        #'data/res_company.xml',
        'data/project_stages.xml'
        
    ],
	'installable': True,
    'application': False,

}



