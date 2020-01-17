# -*- coding: utf-8 -*-
from odoo import http

# class CvEbolivar(http.Controller):
#     @http.route('/cv_ebolivar/cv_ebolivar/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cv_ebolivar/cv_ebolivar/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cv_ebolivar.listing', {
#             'root': '/cv_ebolivar/cv_ebolivar',
#             'objects': http.request.env['cv_ebolivar.cv_ebolivar'].search([]),
#         })

#     @http.route('/cv_ebolivar/cv_ebolivar/objects/<model("cv_ebolivar.cv_ebolivar"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cv_ebolivar.object', {
#             'object': obj
#         })