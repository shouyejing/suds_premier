from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SalesCostRevenue(models.Model):
    _inherit='sale.order'

    
    branch_id = fields.Many2one('branches.cost.center', string="Branch", related='analytic_account_id.branch_id')
    company_name = fields.Char(related="company_id.name", string="Company")
    is_associated_with_project = fields.Boolean(string="Is associated with a project?")
    project_id = fields.Many2one('project.project',string="Project")
    

    @api.multi
    def _prepare_invoice(self):
        res = super(SalesCostRevenue, self)._prepare_invoice()
        res.update({'analytic_account_id': self.analytic_account_id.id})
        return res

    @api.onchange('template_id')
    def onchange_template_id(self):
        if not self.template_id:
            return
        template = self.template_id.with_context(lang=self.partner_id.lang)

        order_lines = [(5, 0, 0)]
        for line in template.quote_line:
            discount = 0
            if self.pricelist_id:
                price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(line.product_id, 1, False)
                if self.pricelist_id.discount_policy == 'without_discount' and line.price_unit:
                    discount = (line.price_unit - price) / line.price_unit * 100
                    price = line.price_unit

            else:
                price = line.price_unit

            data = {
                'name': line.name,
                'date_of_pickup': line.date_of_pickup,
                'shift': line.shift,
                'delivery_date': line.delivery_date,
                'department_id': line.department_id.id,
                'price_unit': price,
                'discount': 100 - ((100 - discount) * (100 - line.discount)/100),
                'product_uom_qty': line.product_uom_qty,
                'product_id': line.product_id.id,
                'layout_category_id': line.layout_category_id,
                'product_uom': line.product_uom_id.id,
                'website_description': line.website_description,
                'state': 'draft',
                'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
            }
            if self.pricelist_id:
                data.update(self.env['sale.order.line']._get_purchase_price(self.pricelist_id, line.product_id, line.product_uom_id, fields.Date.context_today(self)))
            order_lines.append((0, 0, data))

        self.order_line = order_lines
        self.order_line._compute_tax_id()

        option_lines = []
        for option in template.options:
            if self.pricelist_id:
                price = self.pricelist_id.with_context(uom=option.uom_id.id).get_product_price(option.product_id, 1, False)
            else:
                price = option.price_unit
            data = {

                'product_id': option.product_id.id,
                'layout_category_id': option.layout_category_id,
                'name': option.name,
                'quantity': option.quantity,
                'uom_id': option.uom_id.id,
                'price_unit': price,
                'discount': option.discount,
                'website_description': option.website_description,
            }
            option_lines.append((0, 0, data))
        self.options = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.to_string(datetime.now() + timedelta(template.number_of_days))

        self.website_description = template.website_description
        self.require_payment = template.require_payment

        if template.note:
            self.note = template.note

class SalesOrderLineAquion(models.Model):
    _inherit='sale.order.line'

    date_of_pickup = fields.Date(string="Date of Pickup", store=True)
    shift = fields.Selection(selection=[
        ('AM', 'AM'),
        ('PM', 'PM')
    ],string="Shift", store=True)
    delivery_date = fields.Date(String="Delivery Date", store=True)
    department_id = fields.Many2one('aquion.department', string="Department", store=True)

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SalesOrderLineAquion, self)._prepare_invoice_line(qty)
        res.update({'date_of_pickup': self.date_of_pickup,
                    'shift': self.shift,
                    'delivery_date': self.delivery_date,
                    'department_id': self.department_id.id})
        return res

    

class QuoteTemplateAquion(models.Model):
    _inherit='sale.quote.template'

    delivery_date = fields.Date(string="Delivery Date")
    date_of_pickup = fields.Date(string="Date of Pickup")
    shift = fields.Selection(selection=[
        ('AM', 'AM'),
        ('PM', 'PM')
    ],string="Shift")

class QuoteTemplateLine(models.Model):
    _inherit='sale.quote.line'

    delivery_date = fields.Date(string="Delivery Date")
    department_id = fields.Many2one('aquion.department', string="Department")
    date_of_pickup = fields.Date(string="Date of Pickup")
    shift = fields.Selection(selection=[
        ('AM', 'AM'),
        ('PM', 'PM')
    ],string="Shift")
    layout_category_id = fields.Many2one('sale.layout_category', string="Section", compute='_create_section')

    @api.depends('date_of_pickup', 'shift')
    def _create_section(self):
        for i in self:
            if i.date_of_pickup and i.shift:
                section_shift_exists = self.env['sale.layout_category'].search([('name', '=', str(i.date_of_pickup) + ' ' + i.shift)])
                if section_shift_exists:
                    i.layout_category_id = section_shift_exists.id
                else:
                    section_shift = self.env['sale.layout_category'].create({'name': str(i.date_of_pickup) + ' ' + i.shift})
                    i.layout_category_id = section_shift.id


class AquionDepartment(models.Model):
    _name='aquion.department'

    name = fields.Char(string="Name", required=True)

class SalesInvoiceCostRevenue(models.Model):
    _inherit='account.invoice'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    branch_id = fields.Many2one('branches.cost.center', string="Branch", related='analytic_account_id.branch_id')
    company_name = fields.Char(related="company_id.name", string="Company")
    is_royalty_fee = fields.Boolean()
    received_by = fields.Char(string="Received By")

    @api.multi
    def _get_dr_report_name(self):
        self.ensure_one()
        return  self.type == 'out_invoice' and self.state == 'draft' and _('Delivery Receipt') or \
                self.type == 'out_invoice' and self.state in ('open','paid') and _('Delivery Receipt - %s') % (self.number)
    
    @api.multi
    def _get_service_invoice(self):
        self.ensure_one()
        return self.type == 'out_invoice' and self.state == 'draft' and _('Service Invoice') or \
                self.type == 'out_invoice' and self.state in ('open','paid') and _('Service Invoice - %s') % (self.number)
    
    


    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
            self.analytic_account_id = self.purchase_id.account_analytic_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.payment_term_id = self.purchase_id.payment_term_id
        self.env.context = dict(self.env.context, from_purchase_order_change=True)
        self.purchase_id = False
        return {}

class InvoiceRoyaltyFee(models.Model):
    _inherit='account.invoice.line'

    month = fields.Many2one('royalty.fee.month', string="Month")
    date_of_pickup = fields.Date(string="Date of Pickup")
    shift = fields.Selection(selection=[
        ('AM', 'AM'),
        ('PM', 'PM')
    ],string="Shift")
    delivery_date = fields.Date(String="Delivery Date")
    department_id = fields.Many2one('aquion.department', string="Department")
    company_name = fields.Char(related="company_id.name", string="Company")

class ProductAnalyticAccount(models.Model):
    _inherit='product.template'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", domain="[('company_id', '=', company_id)]")
    company_name = fields.Char(related="company_id.name", string="Company")