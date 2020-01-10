from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class FranchiseeProfile(models.Model):
    _inherit = 'res.partner'

    TAX_TYPE = [
        ('registered', 'VAT REGISTERED'),
        ('non_vat', 'NON VAT'),
    ]

    date_opened = fields.Date(string="Date Opened")
    manager_name = fields.Char(string="Manager/Partner Name")
    manager_contact_no = fields.Char(string="Manager/Partner Contact/s")
    manager_email_address = fields.Char("Manager Email Address")
    shop_email_address = fields.Char("Shop Email Address")
    shop_phone = fields.Char(string="Shop's Landline Number")
    shop_mobile = fields.Char(string="Shop's Official Mobile Number")
    fb_page = fields.Char(string="Facebook page")
    instagram_account = fields.Char(string="Instagram account")
    twitter_account = fields.Char(string="Twitter account")
    branch_id = fields.Many2one('branches.cost.center', string="Branch")
    business_name = fields.Char(string="Business Name")
    franchisee_company_name = fields.Char(related="parent_id.name")
    tax_type = fields.Selection(
        TAX_TYPE, string="Tax Type", default="non_vat",required=True)
