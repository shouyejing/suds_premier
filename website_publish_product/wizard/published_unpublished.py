# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class ProductPublished(models.TransientModel):

    _name = 'product.published'

    state = fields.Selection([('published', 'Published'), ('unpublished', 'Unpublished')], default='published', string='Publish/Unpublish')

    @api.multi
    def publish_product(self):
        active_ids = self.env['product.template'].browse(self.env.context.get('active_ids'))
        if self.state == 'published':
            active_ids.write({'website_published': True})
        elif self.state == 'unpublished':
            active_ids.write({'website_published': False})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
