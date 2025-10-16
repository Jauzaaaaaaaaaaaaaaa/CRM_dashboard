from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime, date
import logging

_logger = logging.getLogger(__name__)

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

    # Timestep fields
    timestep_deadline = fields.Date(
        string="Timestep Deadline",
        help="Deadline when this lead should be recycled (created_date + 90 days).",
        copy=False,
        index=True,
    )
    last_timestep_notification = fields.Date(
        string="Last Timestep Notification",
        help="Date when the last timestep notification was sent to the salesperson.",
        copy=False,
    )
    timestep_recycled = fields.Boolean( #cek logika saat keluar dari recycle, hilangkan tanda flag, notifikasi masih eror (solve, double check)
        string="Recycled by Timestep",
        help="Technical flag marking if the lead was moved to Recycle by timestep logic.",
        copy=False,
        index=True,
    )
    note_timestep = fields.Text(string="Timestep Notes", copy=False)
    # ---------- Display/format fields (computed) ----------
    # timestep_deadline_ddmmyyyy = fields.Char(
    #     string="Recycle Deadline (DD/MM/YYYY)",
    #     compute='_compute_timestep_deadline_display',
    #     store=False,
    #     readonly=True,
    # )
    timestep_deadline_long = fields.Char(
        string="Recycle Deadline",
        compute='_compute_timestep_deadline_display',
        store=False,
        readonly=True,
        help="Human friendly format with month name in Indonesian, e.g. 10 Oktober 2025"
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

    @api.depends('timestep_deadline')
    def _compute_timestep_deadline_display(self):
        """Compute display-friendly strings for timestep_deadline.

        - dd/mm/yyyy: '10/10/2025'
        - long: '10 Oktober 2025'  (month names in Indonesian)
        """
        # mapping month number -> Indonesian month name
        month_names = {
            1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
            5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
        }
        for rec in self:
            ddmm = ''
            long = ''
            if rec.timestep_deadline:
                # rec.timestep_deadline is a string 'YYYY-MM-DD'
                try:
                    # safe parse
                    d = fields.Date.from_string(rec.timestep_deadline)
                    # build dd/mm/yyyy
                    dd = f"{d.day:02d}"
                    mm = f"{d.month:02d}"
                    yyyy = f"{d.year}"
                    ddmm = f"{dd}/{mm}/{yyyy}"
                    # long format with month name
                    month_name = month_names.get(d.month, str(d.month))
                    long = f"{dd} {month_name} {yyyy}"
                except Exception:
                    # fallback: raw value
                    ddmm = rec.timestep_deadline or ''
                    long = rec.timestep_deadline or ''
            else:
                ddmm = ''
                long = ''
            # rec.timestep_deadline_ddmmyyyy = ddmm
            rec.timestep_deadline_long = long

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # compute default deadline if not set
            if not rec.timestep_deadline:
                # prefer rec.create_date (datetime string) if available
                try:
                    created_dt = rec.create_date or fields.Datetime.now()
                    created_date = fields.Datetime.from_string(created_dt).date()
                except Exception:
                    created_date = fields.Date.context_today(rec)
                rec.sudo().write({'timestep_deadline': created_date + timedelta(days=90)})
        return records

    # --------------- utility: map crm.lead.activitytype -> mail.activity.type ---------------
    # def _ensure_mail_activity_type_for(self, activity_type_record):
    #     """Given a crm.lead.activitytype record, find or create an equivalent mail.activity.type."""
    #     MailActivityType = self.env['mail.activity.type'].sudo()
    #     name = (activity_type_record.name or 'Timestep Followup').strip()
    #     if not name:
    #         name = 'Timestep Followup'
    #     existing = MailActivityType.search([('name', '=', name)], limit=1)
    #     if existing:
    #         return existing
    #     # create new mail.activity.type
    #     try:
    #         new = MailActivityType.create({
    #             'name': name,
    #             'summary': f"Activity for {name}",
    #         })
    #         return new
    #     except Exception as e:
    #         _logger.exception("Failed to create mail.activity.type for %s: %s", name, e)
    #         return None
    def _ensure_mail_activity_type_for(self, activity_type_record):
        """Map crm.lead.activitytype -> mail.activity.type safely."""
        MailActivityType = self.env['mail.activity.type'].sudo()
        name = (activity_type_record.name or 'Timestep Followup').strip()
        if not name:
            name = 'Timestep Followup'
        try:
            existing = MailActivityType.search([('name', '=', name)], limit=1)
        except Exception as e:
            _logger.exception("Error searching mail.activity.type: %s", e)
            existing = None
        if existing:
            return existing
        # create new mail.activity.type (minimal)
        try:
            new = MailActivityType.create({
                'name': name,
                # 'summary' optional but useful
                'summary': f"Timestep: {name}",
            })
            return new
        except Exception as e:
            _logger.exception("Failed to create mail.activity.type for %s: %s", name, e)
            return None


    # --------------- create mail.activity (safe, avoid duplicates) ---------------
    # def _create_mail_activity_safe(self, lead, mail_activity_type, user, summary, note, deadline=None):
    #     """
    #     Create a mail.activity for lead if there's no existing pending activity of same type and user.
    #     mail_activity_type: record (mail.activity.type)
    #     user: res.users
    #     """
    #     Activity = self.env['mail.activity'].sudo()
    #     domain = [
    #         ('res_model', '=', 'crm.lead'),
    #         ('res_id', '=', lead.id),
    #         ('user_id', '=', user.id),
    #         ('activity_type_id', '=', mail_activity_type.id),
    #         ('state', '!=', 'done'),
    #     ]
    #     exists = Activity.search(domain, limit=1)
    #     if exists:
    #         # skip duplicate
    #         return exists
    #     vals = {
    #         'res_id': lead.id,
    #         'res_model': 'crm.lead',
    #         'activity_type_id': mail_activity_type.id,
    #         'user_id': user.id,
    #         'summary': summary,
    #         'note': note or '',
    #         'date_deadline': deadline or fields.Date.context_today(lead),
    #     }
    #     try:
    #         act = Activity.create(vals)
    #         return act
    #     except Exception as e:
    #         _logger.exception("Failed to create mail.activity: %s", e)
    #         return None
    def _create_mail_activity_safe(self, lead, mail_activity_type, user, summary, note, deadline=None):
        """Create a mail.activity for lead if there's no existing pending activity of same type and user.
        This version is robust: checks available fields, uses sudo, catches exceptions.
        """
        Activity = self.env['mail.activity'].sudo()

        # Build domain to check pending activities robustly (try to use res_model_id if available)
        domain = [
            ('user_id', '=', user.id),
            ('activity_type_id', '=', mail_activity_type.id),
            ('state', '!=', 'done'),
        ]
        # prefer res_model_id if exists
        if 'res_model_id' in Activity._fields:
            model_id = self.env['ir.model']._get('crm.lead').id
            domain.append(('res_model_id', '=', model_id))
            domain.append(('res_id', '=', lead.id))
        else:
            domain.append(('res_model', '=', 'crm.lead'))
            domain.append(('res_id', '=', lead.id))

        try:
            exists = Activity.search(domain, limit=1)
        except Exception as e:
            _logger.exception("Error searching mail.activity: %s", e)
            exists = False

        if exists:
            return exists

        vals = {
            'res_id': lead.id,
            'activity_type_id': mail_activity_type.id,
            'user_id': user.id,
            'summary': summary,
            'note': note or '',
            'date_deadline': deadline or fields.Date.context_today(lead),
        }
        # set res_model or res_model_id depending on model
        if 'res_model_id' in Activity._fields:
            vals['res_model_id'] = self.env['ir.model']._get('crm.lead').id
        else:
            vals['res_model'] = 'crm.lead'

        try:
            act = Activity.create(vals)
            return act
        except Exception as e:
            _logger.exception("Failed to create mail.activity (safe): %s. vals=%s", e, vals)
            return None


    # --------------- get or create Recycle stage ---------------
    def _get_or_create_recycle_stage(self):
        Stage = self.env['crm.stage'].sudo()
        recycle = Stage.search([('name', '=', 'Recycle')], limit=1)
        if recycle:
            return recycle
        # create default Recycle stage
        try:
            return Stage.create({
                'name': 'Recycle',
                'sequence': 1000,
                'fold': True,
            })
        except Exception as e:
            _logger.exception("Failed to create Recycle stage: %s", e)
            return False

    # --------------- cron entrypoint ---------------
    # @api.model
    # def cron_process_timestep_leads(self):
    #     """Daily cron to:
    #      - move expired leads to Recycle
    #      - send follow-up activities based on activity_type_ids
    #     """
    #     today = fields.Date.context_today(self)
    #     Lead = self.env['crm.lead'].sudo()
    #     domain = [
    #         ('type', '=', 'opportunity'),
    #         ('active', '=', True),
    #         ('timestep_recycled', '=', False),
    #     ]
    #     leads = Lead.search(domain)
    #     if not leads:
    #         return True

    #     recycle_stage = self._get_or_create_recycle_stage()
    #     for lead in leads:
    #         # ensure deadline
    #         if not lead.timestep_deadline:
    #             try:
    #                 created_dt = lead.create_date or fields.Datetime.now()
    #                 created_date = fields.Datetime.from_string(created_dt).date()
    #             except Exception:
    #                 created_date = fields.Date.context_today(lead)
    #             lead.sudo().write({'timestep_deadline': created_date + timedelta(days=90)})

    #         # calc days left
    #         try:
    #             deadline = fields.Date.from_string(lead.timestep_deadline)
    #         except Exception:
    #             deadline = fields.Date.context_today(lead) + timedelta(days=90)
    #         days_until = (deadline - fields.Date.context_today(lead)).days

    #         # expired -> move to Recycle
    #         if days_until < 0:
    #             if recycle_stage:
    #                 try:
    #                     lead.sudo().write({
    #                         'stage_id': recycle_stage.id,
    #                         'timestep_recycled': True,
    #                         'note_timestep': (lead.note_timestep or '') + "\nMoved to Recycle by Timestep on %s" % fields.Date.context_today(lead)
    #                     })
    #                     lead.sudo().message_post(body=f"Lead moved to Recycle by Timestep automation on {fields.Date.context_today(lead)}.")
    #                 except Exception as e:
    #                     _logger.exception("Failed moving lead %s to Recycle: %s", lead.id, e)
    #             continue

    #         # decide notification interval
    #         interval = 3 if days_until <= 30 else 7

    #         # determine if we should send (per lead-level last notification)
    #         send_lead_level = False
    #         if not lead.last_timestep_notification:
    #             send_lead_level = True
    #         else:
    #             try:
    #                 last = fields.Date.from_string(lead.last_timestep_notification)
    #                 if (fields.Date.context_today(lead) - last).days >= interval:
    #                     send_lead_level = True
    #             except Exception:
    #                 send_lead_level = True

    #         # If lead has activity_type_ids, create activities per each activity type.
    #         # Otherwise create a generic "Timestep Followup" activity.
    #         if lead.user_id and send_lead_level:
    #             if lead.activity_type_ids:
    #                 for atype in lead.activity_type_ids:
    #                     # map to mail.activity.type
    #                     mail_at = self._ensure_mail_activity_type_for(atype)
    #                     if not mail_at:
    #                         continue
    #                     # create only if not exists pending
    #                     summary = f"{mail_at.name} — Timestep reminder"
    #                     note = (
    #                         f"Please follow up this lead. Deadline for recycle: {lead.timestep_deadline} "
    #                         f"({days_until} days left). Interval: every {interval} days."
    #                     )
    #                     self._create_mail_activity_safe(lead, mail_at, lead.user_id, summary, note,
    #                                                    deadline=fields.Date.context_today(lead))
    #             else:
    #                 # generic fallback
    #                 MailActivityType = self.env['mail.activity.type'].sudo()
    #                 generic = MailActivityType.search([('name', '=', 'Timestep Followup')], limit=1)
    #                 if not generic:
    #                     generic = MailActivityType.create({'name': 'Timestep Followup', 'summary': 'Timestep follow-up'})
    #                 summary = "Timestep follow-up reminder"
    #                 note = f"Please follow up this lead. Deadline for recycle: {lead.timestep_deadline} ({days_until} days left)."
    #                 self._create_mail_activity_safe(lead, generic, lead.user_id, summary, note,
    #                                                deadline=fields.Date.context_today(lead))

    #             # update last notification date after creating activities
    #             try:
    #                 lead.sudo().write({'last_timestep_notification': fields.Date.context_today(lead)})
    #             except Exception:
    #                 _logger.exception("Failed updating last_timestep_notification for %s", lead.id)

    #     return True
    @api.model
    def cron_process_timestep_leads(self):
        """Robust daily cron runner for timestep logic. Handles errors per-lead and logs them."""
        Lead = self.env['crm.lead'].sudo()
        domain = [
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('timestep_recycled', '=', False),
        ]
        leads = Lead.search(domain)
        if not leads:
            return True

        # attempt to obtain recycle stage once (but still protect creation)
        try:
            recycle_stage = self._get_or_create_recycle_stage()
        except Exception as e:
            _logger.exception("Failed to get/create recycle stage: %s", e)
            recycle_stage = False

        today = fields.Date.context_today(self)

        for lead in leads:
            try:
                # ensure deadline exists
                if not lead.timestep_deadline:
                    try:
                        created_dt = lead.create_date or fields.Datetime.now()
                        created_date = fields.Datetime.from_string(created_dt).date()
                    except Exception:
                        created_date = today
                    # write with sudo to avoid access problems
                    lead.sudo().write({'timestep_deadline': created_date + timedelta(days=90)})

                # compute days left (ensure valid date)
                try:
                    deadline = fields.Date.from_string(lead.timestep_deadline)
                except Exception:
                    deadline = today + timedelta(days=90)
                days_until = (deadline - today).days

                # If deadline passed -> move to recycle
                if days_until < 0:
                    if recycle_stage:
                        try:
                            lead.sudo().write({
                                'stage_id': recycle_stage.id,
                                'timestep_recycled': True,
                                'note_timestep': (lead.note_timestep or '') + f"\nMoved to Recycle by Timestep on {today}"
                            })
                            lead.sudo().message_post(body=f"Lead moved to Recycle by Timestep automation on {today}.")
                        except Exception as e:
                            _logger.exception("Failed moving lead %s to Recycle: %s", lead.id, e)
                    # done for this lead
                    continue

                # decide notification interval
                interval = 3 if days_until <= 30 else 7

                # should send check
                send = False
                last = lead.last_timestep_notification
                if not last:
                    send = True
                else:
                    try:
                        last_date = fields.Date.from_string(last)
                        if (today - last_date).days >= interval:
                            send = True
                    except Exception:
                        send = True

                if send and lead.user_id:
                    # create activities based on activity_type_ids if present
                    if lead.activity_type_ids:
                        for atype in lead.activity_type_ids:
                            try:
                                mail_at = self._ensure_mail_activity_type_for(atype)
                                if not mail_at:
                                    continue
                                summary = f"{mail_at.name} — Timestep reminder"
                                note = (f"Please follow up this lead. Deadline for recycle: {lead.timestep_deadline} "
                                        f"({days_until} days left). Interval: every {interval} days.")
                                self._create_mail_activity_safe(lead, mail_at, lead.user_id, summary, note,
                                                            deadline=today)
                            except Exception as e:
                                _logger.exception("Error creating activity for lead %s and atype %s: %s", lead.id, getattr(atype, 'name', False), e)
                    else:
                        try:
                            MailActivityType = self.env['mail.activity.type'].sudo()
                            generic = MailActivityType.search([('name', '=', 'Timestep Followup')], limit=1)
                            if not generic:
                                generic = MailActivityType.create({'name': 'Timestep Followup', 'summary': 'Timestep follow-up'})
                            summary = "Timestep follow-up reminder"
                            note = f"Please follow up this lead. Deadline for recycle: {lead.timestep_deadline} ({days_until} days left)."
                            self._create_mail_activity_safe(lead, generic, lead.user_id, summary, note, deadline=today)
                        except Exception as e:
                            _logger.exception("Error creating generic activity for lead %s: %s", lead.id, e)

                    # update last_timestep_notification
                    try:
                        lead.sudo().write({'last_timestep_notification': today})
                    except Exception as e:
                        _logger.exception("Failed updating last_timestep_notification for %s: %s", lead.id, e)

            except Exception as e:
                # catch ANY error for this lead and continue processing next
                _logger.exception("Unhandled error while processing lead %s in cron_process_timestep_leads: %s", lead.id, e)
                # continue to next lead without raising
                continue

        return True



    # --------------- manual buttons ---------------
    def action_force_recycle_by_timestep(self):
        recycle_stage = self._get_or_create_recycle_stage()
        for rec in self:
            if recycle_stage:
                rec.sudo().write({
                    'stage_id': recycle_stage.id,
                    'timestep_recycled': True,
                    'note_timestep': (rec.note_timestep or '') + "\nManually forced to Recycle on %s" % fields.Date.context_today(rec)
                })
                rec.sudo().message_post(body="Manually forced to Recycle by user.")
        return True

    def action_recompute_timestep_deadline(self):
        for rec in self:
            try:
                created_dt = rec.create_date or fields.Datetime.now()
                created_date = fields.Datetime.from_string(created_dt).date()
            except Exception:
                created_date = fields.Date.context_today(rec)
            rec.sudo().write({'timestep_deadline': created_date + timedelta(days=90)})
        return True








    # lead_count = fields.Integer(string='Lead Count', compute='_compute_lead_count', store=False)

    # def _compute_lead_count(self):
    #     for stage in self:
    #         stage.lead_count = self.env['crm.lead'].search_count([('stage_id', '=', stage.id)])