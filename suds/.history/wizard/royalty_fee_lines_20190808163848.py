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
    segment_id = fields.Many2one('segment.cost.center', string="Segment")
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)

    @api.model
    def _prepare_item(self, line):
        return {
            'royalty_fee_lines_id': line.id,
            'month': line.month.id,
            'royalty_fee': line.subtotal,
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
    def _prepare_royalty_invoice_line(self, line):
        return {
                'product_id.name': 'Royalty Fee',
                'month': line.month,
                'price_unit':line.royalty_fee,
                }

    @api.multi
    def make_royalty_line_invoice(self):
        # res=[]
        # if not self.royalty_fee_to_invoice_ids:
        #     raise UserError(_('No lines/royalty fee to invoice'))
        items=[]
        for line in self.royalty_fee_to_invoice_ids:
            items.append([6, 0, self._prepare_royalty_invoice_line(line)])
        
        create_invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_id.id,
            'is_royalty_fee': True,
            'segment_id': self.segment_id.id,
            'date_invoice': datetime.now(),
        })

        created_invoice = self.env['account.invoice'].browse(create_invoice.id)
        _logger.info("\n\n\n res %s \n\n\n\n" % (created_invoice.id))
        for line in self.royalty_fee_to_invoice_ids:
            for invoice_lines in created_invoice.invoice_line_ids:
                created_invoice.write({'invoice_line_ids': [(0,0,{
                    'product_id.name': 'Royalty Fee',
                    'month': line.month,
                    'price_unit':line.royalty_fee,
                    'invoice_id': create_invoice.id
                })]
        })
        #action.partner_id.name = "Agrolait"
        #return action
        
        
        return {
                'name': _('Invoice'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'res_id': created_invoice.id,
                'context': create_invoice.id,
                'type': 'ir.actions.act_window'
            }

class RoyaltyFeeLinestoInvoice(models.TransientModel):
    _name = 'royalty.fee.lines.to.invoice'

    royalty_fee_lines_id = fields.Many2one('royalty.fee.to.invoice')
    month = fields.Many2one('royalty.fee.month', string="Month")
    royalty_fee = fields.Float(string="Royalty Fee")



