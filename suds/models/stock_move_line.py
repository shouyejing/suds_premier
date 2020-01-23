from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    origin = fields.Char(string="Origin", compute="_get_origin_document")

    @api.depends('picking_id')
    def _get_origin_document(self):
        for rec in self:
            rec.origin = rec.picking_id.origin
        return True