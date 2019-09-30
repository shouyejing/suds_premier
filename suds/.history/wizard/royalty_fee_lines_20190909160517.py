from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class RoyaltyFeetoInvoice(models.TransientModel):
    _name='royalty.fee.to.invoice'

    royalty_fee_to_invoice_ids = fields.One2many('royalty.fee.lines.to.invoice','royalty_fee_lines_id', string="Royalty Fee to Invoice")
    is_royalty_fee = fields.Boolean(default=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)

    @api.model
    def _prepare_item(self, line):
        return {
            'royalty_fee_lines_id': line.id,
            'month': line.month.id,
            'royalty_fee': line.subtotal,
            'swp': line.swp
        }

    @api.model
    def default_get(self, fields):
        res = super(RoyaltyFeetoInvoice, self).default_get(fields)
        request_line_obj = self.env['monthly.royalty.fees.line']
        request_line_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if not request_line_ids:
            return res
        assert active_model == 'monthly.royalty.fees.line', \
            'Bad context propagation'

        items = []
        for line in request_line_obj.browse(request_line_ids):
            items.append([0, 0, self._prepare_item(line)])
        res['royalty_fee_to_invoice_ids'] = items
        return res

    @api.model
    def _prepare_customer_invoice(self, picking_type_id,
                                      company_id):
        data = {
            'origin': '',
            'picking_type_id': picking_type_id,
            'company_id': company_id,
            }
        return data

    @api.multi
    def _prepare_royalty_invoice_line_royalty_fee(self, line):
        return {
                'product_id.name': 'Royalty Fee',
                'month': line.month.id,
                'quantity': 1,
                'name': 'Royalty Fee',
                'price_unit':line.royalty_fee,
                'price_subtotal': line.royalty_fee,
                }

    @api.multi
    def _prepare_royalty_invoice_line_swp(self, line):
        return {
                'product_id.name': 'SWP',
                'month': line.month.id,
                'quantity': 1,
                'name': 'System Wide Payment Fee',
                'price_unit':line.swp,
                'price_subtotal': line.swp,
                }

    @api.multi
    def make_royalty_line_invoice(self):
        view_id = self.env.ref('account.invoice_form')
        invoice_fees=[]
        for line in self.royalty_fee_to_invoice_ids:
            invoice_fees.append([0, 0, self._prepare_royalty_invoice_line_royalty_fee(line)])
            invoice_fees.append([0, 0, self._prepare_royalty_invoice_line_swp(line)])

        
        return {
            'name': _('Invoice Royalty Fees'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],
            'context': {
                    'default_invoice_line_ids': invoice_fees,
                    'default_state': 'draft',
                    'default_partner_id': self.partner_id.id,
                    'default_is_royalty_fee': True,
                    'default_date_invoice': datetime.now(),
                    'default_name': '',
                    }
            }
     
        
        

class RoyaltyFeeLinestoInvoice(models.TransientModel):
    _name = 'royalty.fee.lines.to.invoice'

    royalty_fee_lines_id = fields.Many2one('royalty.fee.to.invoice')
    month = fields.Many2one('royalty.fee.month', string="Month")
    royalty_fee = fields.Float(string="Royalty Fee")
    swp = fields.Float(string="SWP")



