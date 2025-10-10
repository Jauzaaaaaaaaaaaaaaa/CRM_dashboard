from odoo import fields, models, api, _
from odoo.exceptions import UserError

class CRMLead(models.Model):
    _inherit = "crm.lead"

    # lead_category_id = fields.Many2one('crm.lead.category', string='Lead Category')

    batteray_qty = fields.Char('Battery Qty')
    # closing_date = fields.Date('Estimasi Closing Date')
    segmentation_id = fields.Many2one('crm.lead.segmentation', string='Leads Segmentation')
    lead_type_id = fields.Many2one('crm.lead.type', string='Leads Type')
    source_id = fields.Many2one('crm.lead.source', string='Source of Leads')
    product_potential_ids = fields.Many2many(
        'crm.lead.productpotential',
        'crm_lead_productpotential_rel',
        'lead_id', 'product_id',
        string='Product Potential'
    )
    activity_type_ids = fields.Many2many(
        'crm.lead.activitytype',
        'crm_lead_activitytype_rel',
        'lead_id', 'activity_id',
        string='Activity Type'
    )
    # Priority selection (Low/Middle/High) that maps to builtin priority (stars)
    priority_level = fields.Selection(
        [('low', 'Low'), ('middle', 'Middle'), ('high', 'High')],
        string='Priority Level',
        default='middle',
        help="Select priority level to automatically set the star rating (priority)."
    )

    competitor_id = fields.Many2one('crm.lead.competitor', string='Competitor Name')
    competitor_brand_id = fields.Many2one('crm.lead.brandcompetitor', string='Brand Competitor')
    competitor_product_id = fields.Many2one('crm.lead.productcompetitor', string='Product Competitor')
    notes_competitor = fields.Char('Notes Competitor')
    price_competitor = fields.Monetary('Price of Competitor', currency_field='company_currency')

    notes = fields.Char('Notes')

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    @api.onchange('priority_level')
    def _onchange_priority_level(self):
        """Automatically adjust 'priority' (star rating) based on 'priority_level'."""
        mapping = {'low': '1', 'middle': '2', 'high': '3'}
        for rec in self:
            rec.priority = mapping.get(rec.priority_level or 'low', '1')

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure priority matches priority_level on create."""
        mapping = {'low': '1', 'middle': '2', 'high': '3'}
        for vals in vals_list:
            level = vals.get('priority_level', 'low')
            vals['priority'] = mapping.get(level, '1')
        return super().create(vals_list)

    def write(self, vals):
        """Ensure priority stays synced if priority_level changes."""
        mapping = {'low': '1', 'middle': '2', 'high': '3'}
        res = super().write(vals)
        if 'priority_level' in vals:
            for rec in self:
                rec.priority = mapping.get(rec.priority_level or 'low', '1')
        return res










    # lead_count = fields.Integer(string='Lead Count', compute='_compute_lead_count', store=False)

    # def _compute_lead_count(self):
    #     for stage in self:
    #         stage.lead_count = self.env['crm.lead'].search_count([('stage_id', '=', stage.id)])