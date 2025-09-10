from odoo import models, fields, api,_
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    tag_ids = fields.Many2many(comodel_name='crm.tag',string="Tags")
        # relation='sale_order_tag_rel', column1='order_id', column2='tag_id',
        