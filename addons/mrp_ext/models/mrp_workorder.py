from odoo import models, fields, api,_
class Mrp_Workorder(models.Model):
    _inherit = 'mrp.workorder'
    pic_id = fields.Many2one('hr.employee', string='PIC Name')