from odoo import models, fields

class CRMLead(models.Model):
    _inherit = "crm.lead"

    # Tambahan field kategori
    lead_category_id = fields.Many2one(
        'crm.lead.category',
        string="Lead Category",
        help="Kategori untuk mengelompokkan lead."
    )

    def action_set_lost(self, lost_reason_id=None):
        """Override agar lead pindah ke stage Lost (bukan Won)."""
        # Jalankan logika asli Odoo (supaya alasan lost tetap tercatat)
        res = super().action_set_lost(lost_reason_id=lost_reason_id)

        # Cari stage Lost (pastikan sudah ada di crm_stage.xml)
        lost_stage = self.env['crm.stage'].search([('name', '=', 'Lost')], limit=1)

        # Update stage semua leads yang dilost
        for lead in self:
            if lost_stage:
                lead.stage_id = lost_stage.id

        return res


class CRMLeadCategory(models.Model):
    _name = "crm.lead.category"
    _description = "Lead Category"

    name = fields.Char(string="Category", required=True)
    description = fields.Text(string="Description")
