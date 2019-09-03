from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SaleToProject(models.TransientModel):
    _name='sale.to.project.wizard'

    sale_order_id = fields.Many2one(string="Sale ID")
    project_name = fields.Char(string="Business Name")
    partner_id = fields.Many2one('res.partner', string="Customer")

    @api.model
    def default_get(self, fields):
        res = super(SaleToProject, self).default_get(fields)
        active_model = self.env.context.get('active_model')

        