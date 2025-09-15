from odoo import models, fields

class CRMStage(models.Model):
    _inherit = "crm.stage"

    is_lost_stage = fields.Boolean(string="Is Lost Stage?", default=False)

