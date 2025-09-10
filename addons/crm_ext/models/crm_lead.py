from odoo import fields, models, _


class CRMLead(models.Model):
    _inherit = "crm.lead"

    lead_category_id = fields.Many2one('crm.lead.category', string='Lead Category')
    lead_count = fields.Integer(string='Lead Count', compute='_compute_lead_count', store=False)

    def _compute_lead_count(self):
        for stage in self:
            stage.lead_count = self.env['crm.lead'].search_count([('stage_id', '=', stage.id)])