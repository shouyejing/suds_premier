from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class CostRevenue(models.Model):
    _inherit='account.analytic.account'

    
    segment_id = fields.Many2one('segment.cost.center', string="Segment")
    branch_id = fields.Many2one('branches.cost.center', string="Branch")
    company_name = fields.Char(related="company_id.name", string="Company")

class DivisionCostCenter(models.Model):
    _name='segment.cost.center'

    name = fields.Char(string='Division Name')

class BranchesCostCenter(models.Model):
    _name='branches.cost.center'

    name = fields.Char(string='Branch Name')