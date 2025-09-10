from odoo import models, fields, api,_
from odoo.exceptions import UserError
class Mrp_Production(models.Model):
    _inherit = 'mrp.production'
    mrp_number= fields.Char('Serial Number',help="Serial Number of Manufacturing Order")
    state = fields.Selection(selection_add=[('delayed', 'Delayed')])
    delay_reason = fields.Text(string="Delay Reason", readonly=True)

    def action_open_delay_wizard(self):
        """Open the wizard to capture delay reason."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production.delay.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_production_id': self.id},
        }

    def action_resume(self):
        """Resume the manufacturing order from 'Delayed' state."""
        for production in self:
            if production.state != 'delayed':
                raise UserError(_("You can only resume orders in the 'Delayed' state."))
            production.state = 'confirmed'
            production.delay_reason=''

