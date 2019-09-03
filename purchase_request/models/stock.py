from odoo import api, fields, models, _, SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_request_id = fields.Many2one('sprogroup.purchase.request', string="Purchase Request Origin")

    @api.multi
    def create_purchase_request(self):
        if self.state in ['waiting', 'confirmed'] and not self.purchase_request_id:
            product_data = []
            for i in self.move_lines:
                if i.product_uom_qty > i.reserved_availability:
                    product_data.append([0, 0, {
                        'product_id': i.product_id.id,
                        'product_uom_id': i.product_uom.id,
                        'product_qty': i.product_uom_qty - i.reserved_availability,
                        # 'date_required': fields.Date.context_today,
                        'company_id': self.company_id.id,
                    }])
            purchase_request = self.env['sprogroup.purchase.request'].create({
                                                                            'name': self.name,
                                                                            'line_ids': product_data,
                                                                            'company_id': self.company_id.id,
                                                                        })
            self.write({'purchase_request_id': purchase_request.id})
            return True
