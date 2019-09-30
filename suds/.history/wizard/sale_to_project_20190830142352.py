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
        sale = self.env['sale.order'].browse(self._context.get('active_id'))
        if not sale.state in ['sale', 'done']:
            raise UserError(_('Please confirm this quotation first before creating the project.'))
        res = super(SaleToProject, self).default_get(fields)
        return res

    @api.multi
    def create_project(self):
        sale = self.env['sale.order'].browse(self._context.get('active_id'))
        project = self.env['project.project'].create({
                                                'name': self.project_name,
                                                'partner_id': sale.partner_id.id
                                            })
        sale.write({'project_id': project.id})
        return {'type': 'ir.actions.act_window_close'}