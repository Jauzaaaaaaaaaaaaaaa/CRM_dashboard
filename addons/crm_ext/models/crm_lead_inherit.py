from odoo import models

class CRMLead(models.Model):
    _inherit = "crm.lead"

    def action_set_lost(self):
        """Override supaya lead pindah otomatis ke stage Lost"""
        res = super(CRMLead, self).action_set_lost()
        lost_stage = self.env['crm.stage'].search([('is_lost_stage', '=', True)], limit=1)
        if lost_stage:
            self.write({'stage_id': lost_stage.id})
        return res
