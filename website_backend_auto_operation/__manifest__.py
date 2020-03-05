# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Website Sale Auto Workflow(Order Confirmation/Invoice Generation/Invoice Payment)",
    "version" : "11.0.0.3",
    "price": 69,
    "currency": 'EUR',
    "category" : "eCommerce",
    "depends" : ['website','website_sale'],
    "author": "BrowseInfo",
    "summary": "This apps helps to make eCommerce Autopayment also generate auto backend Workflow When shop order Process",
    "description": """
    Odoo Website Sale.
    Website Auto Payment , Website Invoice Payment, Website Auto Invoice Payment, Website Auto Order Confirmation, Website Sale Confirmation, Website Order Auto Done, Website Order Auto paid, Invoice Paid from website, 
    Website Auto Confirm Quotation
    Website Auto Create Invoice
    Website Auto Validate Invoice
    Website Auto Create Payment
    Website Confirm Quotation
    Website Confirm Quotation And Create Invoice
    Website Confirm Quotation And Validate Invoice
    WebsiteConfirm Quotation And Validate Invoice and Create Payment
    Website AutoPay in eCommerce
    eCommerce AutoPay
    eCommerce Auto Payment
    eCommerce Auto invoice payment
    Website Backend Auto Operation
    website workflow management
    website automatic workflow
    website configurable workflow
    website auto payment
    website auto invoice
    website auto workflow
    """,
    "website" : "www.browseinfo.in",
    "data": [
        #'security/ir.model.access.csv',
        'views/template.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "live_test_url":'https://youtu.be/go7x4blesSw',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
