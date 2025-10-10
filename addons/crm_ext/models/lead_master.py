from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LeadSegmentation(models.Model):
    _name = "crm.lead.segmentation"
    _description = 'Lead Segmentation'
    _order = 'name'
    
    name = fields.Char('Lead Segmentation', required=True)

class LeadType(models.Model):
    _name = "crm.lead.type"
    _description = 'Lead Type'
    _order = 'name'
    
    name = fields.Char('Lead Type', required=True)

class LeadSource(models.Model):
    _name = "crm.lead.source"
    _description = 'Lead Source'
    _order = 'name'
    
    name = fields.Char('Lead Source', required=True)

class LeadProductPotential(models.Model):
    _name = "crm.lead.productpotential"
    _description = 'Lead Product Potential'
    _order = 'name'
    
    name = fields.Char('Lead Product Potential', required=True)
    color = fields.Integer('Color Index', default=0)

class LeadActivityType(models.Model):
    _name = "crm.lead.activitytype"
    _description = 'Lead Activity Type'
    _order = 'name'
    
    name = fields.Char('Lead Activity Type', required=True)
    color = fields.Integer('Color Index', default=0)

class LeadCompetitor(models.Model):
    _name = "crm.lead.competitor"
    _description = 'Lead Competitor'
    _order = 'name'
       
    name = fields.Char('Competitor')
    
class LeadBrandCompetitor(models.Model):
    _name = "crm.lead.brandcompetitor"
    _description = 'Lead Brand Competitor'
    _order = 'name'
       
    name = fields.Char('Brand Competitor')
    
class LeadProductdCompetitor(models.Model):
    _name = "crm.lead.productcompetitor"
    _description = 'Lead Product Competitor'
    _order = 'name'
       
    name = fields.Char('Product Competitor')
   