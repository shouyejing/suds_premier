from odoo import api, fields, models, _


class DoPurchaseRequisition(models.TransientModel):
    _name = 'do.purchase.requisition'

    @api.model
    def default_get(self, fields):
        res = super(DoPurchaseRequisition, self).default_get(fields)
        data = self.env['sprogroup.purchase.request'].browse(self._context.get('active_ids')[0])
        res['purchase_request_id'] = data.id
        res['line_ids'] = [i.id for i in data.line_ids]
        return res

    action = fields.Selection([
                        ('New', 'Create New'),
                        ('Merge', 'Merge to Existing Request')
                        ], string="Select Action", required=True)
    purchase_requisition_ids = fields.Many2one('purchase.requisition', string="Purchase Requition", domain="[('state', 'in', ['draft'])]")
    purchase_requisition_type_id = fields.Many2one('purchase.requisition.type', string="Agreement Type")
    purchase_request_id = fields.Many2one('sprogroup.purchase.request', string="Purchase Request")
    line_ids = fields.Many2many('sprogroup.purchase.request.line', string="Products", required=True)

    @api.onchange('purchase_requisition_ids')
    def _onchange_purchase_requisition_id(self):
        if self.purchase_requisition_ids:
            self.purchase_requisition_type_id = self.purchase_requisition_ids.type_id.id

    @api.multi
    def create_purchase_requisition(self):
        if self.action in ['New']:
            view_id = self.env.ref('purchase_requisition.view_purchase_requisition_form')
            product_line = []
            for i in self.purchase_request_id.line_ids:
                product_line.append([0, 0, {
                    'product_id': i.product_id.id,
                    'product_qty': i.product_qty,
                    'schedule_date': i.date_required,
                }])
            return {
                'name': _('New Purchase Requition'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.requisition',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'context': {
                        'default_line_ids': product_line,
                        'default_state': 'draft',
                        'default_type_id': self.purchase_requisition_type_id.id,
                        'default_purchase_request_id': self.purchase_request_id.id,
                        }
                    }
        else:
            for i in self.line_ids:
                found = False
                for line in self.purchase_requisition_ids.line_ids:
                    if i.product_id.id == line.product_id.id:
                        line.write({'product_qty': i.product_qty + line.product_qty})
                        self.purchase_requisition_ids.write({
                            'purchase_request_merge_ids': [(4, self.purchase_request_id.id)]
                        })
                        found = True
                        continue
                if not found:
                    self.purchase_requisition_ids.write({
                        'purchase_request_merge_ids': [(4, self.purchase_request_id.id)],
                        'line_ids': [(0, 0, {
                            'product_id': i.product_id.id,
                            'product_qty': i.product_qty,
                            'schedule_date': i.date_required,
                            'product_uom_id': i.product_uom_id.id})]
                    })
            return {'type': 'ir.actions.act_window_close'}
