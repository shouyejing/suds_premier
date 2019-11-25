from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class MonthlyRoyaltyFeeLines(models.Model):
    _name = 'monthly.royalty.fees.line'

    customer_id = fields.Many2one('res.partner', string="Customer")
    tax_type = fields.Selection('res.partner', string="Tax Type", related="customer_id.tax_type",readonly=True)
    month = fields.Many2one('royalty.fee.month', string="Month")
    year = fields.Char(string="Year")
    branch_id = fields.Many2one('branches.cost.center', string="Branch")
    account_id = fields.Many2one('account.account', string="Account")
    gross_amount = fields.Float(
        string="Gross Sales",
        compute="compute_gross_sales",
        store=True
    )
    total_revenue = fields.Float(string="Total Revenue")
    other_additions = fields.Float(string="Other Additions")
    other_deductions = fields.Float(string="Other Deductions")
    sales_tax = fields.Float(
        string="Sales Tax"
    )
    royalty_rate = fields.Float(
        string="Royalty Rate %", compute="compute_royalty_fee", store=True)
    royalty_fee = fields.Float(
        string="Royalty Fee", compute="compute_royalty_fee", store=True)
    vat_sales = fields.Float(
        string="12% VAT", compute="compute_royalty_fee", store=True)
    swp = fields.Float(
        string="SWP 2%", compute="compute_royalty_fee", store=True)
    total_royalty_fee = fields.Float(
        string="Total Royalty Fee", compute="compute_royalty_fee", store=True)
    subtotal = fields.Float(
        string="Subtotal", compute="compute_subtotal", store=True)

    @api.onchange('tax_type','customer_id.tax_type','customer_id','other_additions', 'total_revenue', 'other_deductions')
    def compute_sales_tax(self):
        for rec in self:
            if rec.customer_id.tax_type == 'registered':
                rec.sales_tax = (
                    (rec.total_revenue + rec.other_additions - rec.other_deductions)/1.12)*0.12
            else:
                rec.sales_tax = (
                    rec.total_revenue + rec.other_additions - rec.other_deductions)*0.03

        _logger.info("\n\n\nVals Data: \n%s\n\n\n" %
                     (str(self.sales_tax)))

    @api.depends('other_additions', 'other_deductions', 'sales_tax', 'total_revenue')
    def compute_gross_sales(self):
        for i in self:
            i.gross_amount = i.total_revenue + \
                i.other_additions - i.other_deductions - i.sales_tax

    @api.depends('gross_amount')
    def compute_royalty_fee(self):
        for i in self:
            if (i.gross_amount > 0) and (i.gross_amount <= 200000):
                i.royalty_rate = 3
            elif (i.gross_amount > 200000) and (i.gross_amount <= 250000):
                i.royalty_rate = 4
            elif (i.gross_amount > 250000) and (i.gross_amount <= 300000):
                i.royalty_rate = 5
            else:
                i.royalty_rate = 4
            i.royalty_fee = (i.royalty_rate / 100) * i.gross_amount
            i.vat_sales = i.royalty_fee * 0.12
            i.total_royalty_fee = i.royalty_fee + i.vat_sales
            i.swp = i.gross_amount * 0.02

    @api.depends('total_royalty_fee', 'swp')
    def compute_subtotal(self):
        for i in self:
            i.subtotal = i.total_royalty_fee + i.swp

    # computation of sales tax
    """ =ROUND(-IF($B$2=$Z$1,(((B7+D7+C7)/1.12)*0.12),IF($B$2=$Z$2,((B7+D7+C7)*0.03),0)),2) """


class RoyaltyMonths(models.Model):
    _name = 'royalty.fee.month'

    name = fields.Char(string="Month")
    month_year = fields.Date(string="Date")

class RoyaltyFeeReference(models.Model):
    _name = 'royalty.fee.reference'

    name = fields.Char(string="Rate", default="Rate")
    min_monthly_gross_sales = fields.Float(
        string="Minimum Monthly Gross Sales")
    max_monthly_gross_sales = fields.Float(
        string="Maximum Monthly Gross Sales")
    royalty_fee = fields.Float(
        string="Corresponding Continuing Services and Royalty Fee")
