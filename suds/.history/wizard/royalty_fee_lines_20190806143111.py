from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class RoyaltyFeeLinestoInvoice(models.TransientModel):
    _name='royalty.fee.to.invoice'

    