from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ConfirmQuotation(models.TransientModel):
    _name='batch.confirm.sale.quotation'

    quotation_to_confirm_ids = fields.One2many('quotation.to.confirm', 'quotation_id', readonly=True)

    @api.multi
    def confirm_quotations(self):
        """ confirm the selected quotations """
        for i in self:
            for lines in i.quotation_to_confirm_ids:
                sale_order_id = self.env['sale.order'].search([('name', '=', lines.name)])
                if sale_order_id.state == 'draft':
                    sale_order_id.update({'state': 'done'})
                else:
                    raise UserError('There are quotations that are already confirmed. Please check the quotation status')


    @api.model
    def _prepare_item(self, line):
        return {
            'quotation_id': line.id,
            'name': line.name,
            'partner_id': line.partner_id.id,
            'amount_total': line.amount_total
        }

    @api.model
    def default_get(self, fields):
        res = super(ConfirmQuotation, self).default_get(fields)
        sale_quotation_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
        active_model = self.env.context.get('active_model')

        if not sale_quotation_ids:
            return res
        assert active_model == 'sale.order', \
            'Bad context propagation'

        items = []
        for line in sale_quotation_ids:
            items.append([0, 0, self._prepare_item(line)])
        res['quotation_to_confirm_ids'] = items
        return res

class QuotationToConfirm(models.TransientModel):
    _name='quotation.to.confirm'

    quotation_id = fields.Many2one('batch.confirm.sale.quotation')
    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner')
    amount_total = fields.Float(string="Total")