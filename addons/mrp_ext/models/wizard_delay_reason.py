from odoo import models, fields, api,_
from odoo.exceptions import UserError
class MrpProductionDelayWizard(models.TransientModel):
    _name = 'mrp.production.delay.wizard'
    _description = 'Wizard to Capture Delay Reason'

    production_id = fields.Many2one('mrp.production', string="Manufacturing Order", required=True, readonly=True)
    delay_reason = fields.Text(string="Delay Reason", required=True)

    def action_confirm_delay(self):
        """Confirm the delay and set the state to 'Delayed'."""
        self.ensure_one()
        if not self.delay_reason:
            raise UserError(_("Please provide a reason for the delay."))
        self.production_id.write({
            'state': 'delayed',
            'delay_reason': self.delay_reason,
        })
        return {'type': 'ir.actions.act_window_close'}