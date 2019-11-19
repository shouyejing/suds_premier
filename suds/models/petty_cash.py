# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime as date
from odoo.exceptions import ValidationError, UserError, Warning


class PettyCash(models.Model):
    _inherit = ['petty.cash']

    reason = fields.Char(string='Reason for Petty Cash')
