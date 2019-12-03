from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SalesCostRevenue(models.Model):
    _inherit='sale.order'

    
    branch_id = fields.Many2one('branches.cost.center', string="Branch", related='analytic_account_id.branch_id')
    company_name = fields.Char(related="company_id.name", string="Company")
    is_associated_with_project = fields.Boolean(string="Is associated with a project?")
    project_id = fields.Many2one('project.project',string="Project")
    delivery_date = fields.Date(string="Delivery Date")

    @api.multi
    def _prepare_invoice(self):
        res = super(SalesCostRevenue, self)._prepare_invoice()
        res.update({'analytic_account_id': self.analytic_account_id.id})
        return res

class SalesOrderLineAquion(models.Model):
    _inherit='sale.order.line'

    date_of_pickup = fields.Date(string="Date of Pickup")
    shift = fields.Selection(selection=[
        ('AM', 'AM'),
        ('PM', 'PM')
    ],string="Shift")
    delivery_date = fields.Date(String="Delivery Date")


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
# class SalesInvoiceAquion(models.Model):
#     _inherit='account.invoice.line'

#     date_of_pickup = fields.Date(string="Date of Pickup")
#     shift = fields.Selection(selection=[
#         ('AM', 'AM'),
#         ('PM', 'PM')
#     ],string="Shift")
    
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

class ProductAnalyticAccount(models.Model):
    _inherit='product.template'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", domain="[('company_id', '=', company_id)]")
    company_name = fields.Char(related="company_id.name", string="Company")