from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from datetime import date, datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class ProductAttributesProductTemplate(models.Model):
    _inherit = 'product.template'

    product_item_type_id = fields.Many2one(string='Item Type', comodel_name='product.item.type',
                                       help='Select an item type for this product')
    product_generic_id = fields.Many2one(string='Generic Name', comodel_name='product.generic',
                                       help='Select a generic name for this product')
    size = fields.Float(string="Size/Volume", help="Does not mean Size is equal to Volume. This is only for label purposes.")
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    height = fields.Float(string="Height")
    thickness = fields.Float(string="Thickness")
    size_uom = fields.Many2one(string="Unit of Measure", comodel_name="product.uom")
    length_uom = fields.Many2one(string="Unit of Measure", comodel_name="product.uom")
    width_uom = fields.Many2one(string="Unit of Measure", comodel_name="product.uom")
    height_uom = fields.Many2one(string="Unit of Measure", comodel_name="product.uom")
    thickness_uom = fields.Many2one(string="Unit of Measure", comodel_name="product.uom")

class ProductAttributesGeneric(models.Model):
    _name = 'product.generic'
    _order = 'name'

    name = fields.Char(string='Generic Name', required=True)
    description = fields.Text(string='Description', translate=True)
    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner', ondelete='restrict',
                                 help='Select a partner for this generic name if any.')
    logo = fields.Binary(string='Logo File')
    product_ids = fields.One2many(string='Generic Products', comodel_name='product.template',
                                  inverse_name='product_generic_id')
    products_count = fields.Integer(string='Number of products',compute='compute_products_count')

    @api.multi
    @api.depends('product_ids')
    def compute_products_count(self):
        for record in self:
            record.products_count = len(record.product_ids)

class ProductAttributesItemType(models.Model):
    _name = 'product.item.type'
    _order = 'name'

    name = fields.Char(string='Item Type', required=True)
    description = fields.Text(string='Description', translate=True)
    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner', ondelete='restrict',
                                 help='Select a partner for this generic name if any.')
    logo = fields.Binary(string='Sample Image')
    product_ids = fields.One2many(string='Items', comodel_name='product.template',
                                  inverse_name='product_item_type_id')
    products_count = fields.Integer(string='Number of products',compute='compute_products_count')

    @api.multi
    @api.depends('product_ids')
    def compute_products_count(self):
        for record in self:
            record.products_count = len(record.product_ids)
