from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ProjectStages(models.Model):
    _name='project.stages'

    stage_name = fields.Char(string="Stage Name")