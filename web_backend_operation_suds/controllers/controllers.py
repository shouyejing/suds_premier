# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, http, tools, _
from odoo.http import request
from datetime import datetime
import logging
from odoo.addons.website_sale.controllers.main import WebsiteSale
# from website_backend_auto_operation.controllers.main import OdooWebsiteSale
_logger = logging.getLogger("_name_")


class OdooWebsiteSaleSuds(WebsiteSale):

# When /shop/payment/validate done from backend create sales order, Validate, Create Invoice, Register Payment instead of Quotation...

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        website_order_obj = request.env['res.config.settings']
        website_order_option = website_order_obj.search([], limit=1, order="id desc").website_order_configuration
        
        if transaction_id is None:
            tx = request.website.sale_get_transaction()
            
        else:
            tx = request.env['payment.transaction'].browse(transaction_id)
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if (not order.amount_total and not tx) or tx.state in ['pending', 'done', 'authorized']:
            #if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
            order.with_context(send_email=True).action_confirm()
            #order.force_quotation_send() # Send Mail when order placed from webshop
            order.payment_acquirer_id.website_order_msg = 'confirm'



            # This code is for invoice_policy = order
            item_count = 0
            count = 0
            for item in order.order_line:
                item_count+=1
                if item.product_id.invoice_policy == 'order':
                    count+=1
                if item_count != count:

                    request.website.sale_reset()
                    if tx and tx.state == 'draft':
                        return request.redirect('/shop')

                    return request.redirect('/shop/confirmation')        

            if order.payment_acquirer_id.website_order_configuration == 'invoice':
                self.order_option_invoice()
                order.payment_acquirer_id.website_order_msg = 'invoice'
            elif order.payment_acquirer_id.website_order_configuration == 'validate':
                self.order_option_validate()
                order.payment_acquirer_id.website_order_msg = 'validate'      
            elif order.payment_acquirer_id.website_order_configuration == 'payment':
                self.order_option_payment()
                order.payment_acquirer_id.website_order_msg = 'payment'      
                             
                            
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            order.action_cancel()

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        return request.redirect('/shop/confirmation')
        

    def order_option_invoice(self):
        sale_order_id = None
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        invoice_obj = request.env['account.invoice']
        invoice_lin_obj = request.env['account.invoice.line']
        payment_method = request.env['account.payment.method'].sudo().search([('name','=','Manual')],limit=1)
        partner_obj = request.env['res.partner']
        partner_curr = partner_obj.sudo().browse(order.partner_id.id)
        invoice_id = invoice_obj.sudo().create({
            'partner_id': order.partner_id.id,
            'currency_id': partner_curr.currency_id.id,
            'account_id': partner_curr.property_account_receivable_id.id,
            'origin' : order.name,
            'payment_term_id' : order.payment_term_id.id,
            'user_id' : order.user_id.id,
            'team_id' : order.team_id.id,
        })
        
        for line in order.order_line:
            product_obj = request.env['product.product']
            tax_ids = []
            for tax in line.product_id.taxes_id:
                tax_ids.append(tax.id) 
            vals = {
            'product_id': line.product_id.id,
            'name':line.name,
            'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
            'product_uom_qty': line.product_uom_qty,
            'price_unit':line.price_unit,
            'product_uom':line.product_uom,
            'tax_id': [(6,0,tax_ids)],
            'discount': line.discount,
            'invoice_id': invoice_id.id
            }
            invoice_lin_obj.sudo().create(vals)
        
        if invoice_id:
            for line in order.order_line:
                line.write({'qty_invoiced' : line.product_uom_qty})
        return True

    def order_option_validate(self):

        sale_order_id = None
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        invoice_obj = request.env['account.invoice']
        invoice_lin_obj = request.env['account.invoice.line']
        payment_method = request.env['account.payment.method'].sudo().search([('name','=','Manual')],limit=1)
        partner_obj = request.env['res.partner']
        partner_curr = partner_obj.sudo().browse(order.partner_id.id)
        invoice_id = invoice_obj.sudo().create({
            'partner_id': order.partner_id.id,
            'currency_id': partner_curr.currency_id.id,
            'account_id': partner_curr.property_account_receivable_id.id,
            'origin' : order.name,
            'payment_term_id' : order.payment_term_id.id,
            'user_id' : order.user_id.id,
            'team_id' : order.team_id.id,
        })
        
        for line in order.order_line:
            product_obj = request.env['product.product']
            tax_ids = []
            for tax in line.product_id.taxes_id:
                tax_ids.append(tax.id) 
            vals = {
            'product_id': line.product_id.id,
            'name':line.name,
            'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
            'product_uom_qty': line.product_uom_qty,
            'price_unit':line.price_unit,
            'product_uom':line.product_uom,
            'tax_id': [(6,0,tax_ids)],
            'discount': line.discount,
            'invoice_id': invoice_id.id
            }
            invoice_lin_obj.sudo().create(vals)
        
        if invoice_id:
            for line in order.order_line:
                line.write({'qty_invoiced' : line.product_uom_qty})

        account_search = invoice_obj.sudo().search([('id', '=', invoice_id.id)])

        for a in account_search:
            a.action_date_assign()
            a.action_move_create()
            a.invoice_validate()
        return True

    def order_option_payment(self):
        sale_order_id = None
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')


        invoice_obj = request.env['account.invoice']
        invoice_lin_obj = request.env['account.invoice.line']
        account_payment = request.env['account.payment']
        payment_method = request.env['account.payment.method'].sudo().search([('name','=','Manual')],limit=1)
        partner_obj = request.env['res.partner']
        partner_curr = partner_obj.sudo().browse(order.partner_id.id)
        invoice_id = invoice_obj.sudo().create({
            'partner_id': order.partner_id.id,
            'currency_id': partner_curr.currency_id.id,
            'account_id': partner_curr.property_account_receivable_id.id,
            'origin' : order.name,
            'payment_term_id' : order.payment_term_id.id,
            'user_id' : order.user_id.id,
            'team_id' : order.team_id.id,
        })
        
        for line in order.order_line:
            product_obj = request.env['product.product']
            tax_ids = []
            for tax in line.product_id.taxes_id:
                tax_ids.append(tax.id) 
            vals = {
            'product_id': line.product_id.id,
            'name':line.name,
            'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
            'product_uom_qty': line.product_uom_qty,
            'price_unit':line.price_unit,
            'product_uom':line.product_uom,
            'tax_id': [(6,0,tax_ids)],
            'discount': line.discount,
            'invoice_id': invoice_id.id
            }
            invoice_lin_obj.sudo().create(vals)
        
        if invoice_id:
            for line in order.order_line:
                line.write({'qty_invoiced' : line.product_uom_qty})

        account_search = invoice_obj.sudo().search([('id', '=', invoice_id.id)])

        for a in account_search:
            a.action_date_assign()
            a.action_move_create()
            a.invoice_validate()

        journal = False
        if order.payment_acquirer_id.journal_id:
            journal = order.payment_acquirer_id.journal_id.id
        else:
            request.website.sale_reset()
            if tx and tx.state == 'draft':
                return request.redirect('/shop')
            return request.redirect('/shop/confirmation')

        vals = { 
            'journal_id': journal, 
            'amount':account_search.amount_total, 
            'currency_id': account_search.currency_id.id, 
            'payment_date': datetime.now().date(), 
            'communication': order.name, 
            'payment_type':'inbound', 
            'payment_method_id': 1, 
            'partner_type': 'customer', 
            'partner_id': account_search.partner_id.id,
            'destination_account_id':account_search.account_id.id }
        payment_create = account_payment.sudo().create(vals)
        payment_create.invoice_ids = [(4, account_search.id)]
        validate = payment_create.with_context(destination_account_id=account_search.account_id.id).post()
        account_search.state = 'paid'
        return True
        