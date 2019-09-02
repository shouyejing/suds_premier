from odoo import api, fields, models, _
import math
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class InvoiceSource(models.Model):
    _inherit='account.invoice'

    
    invoice_sales_document = fields.Many2one('sale.order', compute='_get_source', store=True)
    invoice_purchase_document = fields.Many2one('purchase.order', compute='_get_source', store=True)

    @api.one
    @api.depends('origin')
    def _get_source(self):
        if self.type == 'out_invoice':
            invoice_source = self.env['sale.order'].search([('name', '=',self.origin)], limit=1)
            if invoice_source[:1] and invoice_source[:1].state== 'sale': self.invoice_sales_document = invoice_source[:1]
        
        elif self.type == 'in_invoice':
            invoice_source = self.env['purchase.order'].search([('name', '=',self.origin)], limit=1)
            if invoice_source[:1] and invoice_source[:1].state== 'purchase': self.invoice_purchase_document = invoice_source[:1]

class WarehouseSource(models.Model):
    _inherit='stock.picking'

    invoice_purchase_document = fields.Many2one('purchase.order', compute='_get_warehouse_source', store=True)
    invoice_sales_document = fields.Many2one('sale.order', compute='_get_sales_source', store=True)


    
    @api.depends('origin')
    def _get_warehouse_source(self):
        for i in self:
            if i.origin:
                invoice_source = self.env['purchase.order'].search([('name', '=',i.origin)], limit=1)
                if invoice_source[:1] and invoice_source[:1].state== 'purchase': i.invoice_purchase_document = invoice_source[:1]

    @api.depends('origin')
    def _get_sales_source(self):
        for i in self:
            if i.origin:
                invoice_source = self.env['sale.order'].search([('name', '=',i.origin)], limit=1)
                if invoice_source[:1] and invoice_source[:1].state== 'sale': i.invoice_sales_document = invoice_source[:1]