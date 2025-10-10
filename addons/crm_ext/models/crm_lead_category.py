# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class LeadCategory(models.Model):
    _name = "crm.lead.category"
    _description = 'Lead Category'

    name = fields.Char('Description', required=True, translate=True)
    # active = fields.Boolean('Active', default=True)
