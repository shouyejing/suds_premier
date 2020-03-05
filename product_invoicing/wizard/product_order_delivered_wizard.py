# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class InvoicingPolicy(models.TransientModel):

    _name = 'invoicing.policy'

    invoicing_policy = fields.Selection(
        [('order', 'Ordered Quantities'),
         ('delivery', 'Delivered Quantities')],
        default='order',
        string='Invoicing Policy'
    )

    @api.multi
    def set_invoicing_policy(self):
        active_ids = self.env['product.template'].browse(
            self.env.context.get('active_ids'))
        if self.invoicing_policy == 'order':
            active_ids.write({'invoice_policy': 'order'})
        elif self.invoicing_policy == 'delivery':
            active_ids.write({'invoice_policy': 'delivery'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
