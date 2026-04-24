# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author:  Mruthul Raj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import calendar
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.http import request
from odoo.tools import date_utils
from datetime import timedelta



class CRMLead(models.Model):
    """Extends crm.lead for adding more functions in it"""
    _inherit = 'crm.lead'

    monthly_goal = fields.Float(string="Monthly Goal", help="Lead monthly goal")
    achievement_amount = fields.Float(string="Monthly Achievement",
                                      help="Achievement for the month")

    # ============================
    # âœ… ACTIVITY REPORT TOTAL 
    # ============================
    def get_activity_report_total(self):
        self.env.cr.execute("""
            SELECT mat.name, COUNT(*)
            FROM mail_activity ma
            LEFT JOIN mail_activity_type mat ON ma.activity_type_id = mat.id
            WHERE ma.res_model = 'crm.lead'
            GROUP BY mat.name
            ORDER BY COUNT(*) DESC
        """)
        
        rows = self.env.cr.fetchall()

        labels = []
        values = []

        for r in rows:
            raw_name = r[0]

            # âœ… FIX UTAMA DI SINI â€” HANDLE DICT TRANSLATION
            if isinstance(raw_name, dict):
                name = raw_name.get('en_US') or list(raw_name.values())[0]
            elif isinstance(raw_name, str):
                name = raw_name
            else:
                name = "Others"

            labels.append(name)
            values.append(r[1])

        return {
            "labels": labels,
            "values": values,
        }


    def _parse_rpc_kwargs(self, arg):
        """
        Helper aman untuk parse kwargs dari panggilan JSON-RPC Odoo.
        Kadang JS mengirim dalam bentuk args: [{by_all: true}]
        Fungsi ini memastikan hasilnya selalu dict.
        """
        if isinstance(arg, dict):
            return arg
        if isinstance(arg, (list, tuple)) and len(arg) > 0 and isinstance(arg[0], dict):
            return arg[0]
        return {}

    @api.model
    def _get_currency(self):
        """Get the currency symbol and position for the current user's company.
        Returns:
            list: A list containing the currency symbol and its position."""
        currency_array = [self.env.user.company_id.currency_id.symbol,
                          self.env.user.company_id.currency_id.position]
        return currency_array

    @api.model
    def check_user_group(self, kwargs):
        """Checking a user group"""
        user = self.env.user
        if user.has_group('sales_team.group_sale_manager'):
            return True
        else:
            return False
        
    @api.model
    def get_active_leads(self, start_date=None, end_date=None):
        """
        Hitung jumlah Active Leads:
        - active=True
        - belum Won dan belum Lost
        - jika start_date & end_date dikirim, filter berdasarkan create_date
        """
        domain = [
            ('active', '=', True),
            ('stage_id.is_won', '=', False),
            ('stage_id.fold', '=', False),
        ]

        # Jika ada filter tanggal, tambahkan ke domain
        if start_date and end_date:
            domain += [
                ('create_date', '>=', start_date),
                ('create_date', '<=', end_date),
            ]

        count_active = self.env['crm.lead'].search_count(domain)
        return {'active_leads': count_active}
    
    @api.model
    def get_lead_stage_data(self, kwargs = None):
        """funnel chart with Lost included"""
        stage_ids = self.env['crm.stage'].search([], order='sequence asc')
        data = []

        # Hitung lead per stage (tidak lost)
        for stage in stage_ids:
            count = self.search_count([
                ('stage_id', '=', stage.id),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
            ])
            data.append([stage.name, count])

        # Tambahkan Lost
        lost_count = self.search_count([
            ('type', '=', 'opportunity'),
            ('active', '=', False),
        ])
        data.append(['Lost', lost_count])

        return data

    # ================================
    # SOURCE OF LEADS (NEW & ISOLATED)
    # ================================
    @api.model
    def get_source_of_leads(self, kwargs=None):
        """
        Source of Leads berdasarkan crm.lead.source
        Aman, cepat, dan siap untuk chart
        """
        self.env.cr.execute("""
            SELECT
                cls.name AS source_name,
                COUNT(cl.id) AS total
            FROM crm_lead cl
            LEFT JOIN crm_lead_source cls ON cl.source_id = cls.id
            WHERE cl.source_id IS NOT NULL
            GROUP BY cls.name
            ORDER BY COUNT(cl.id) DESC
        """)

        rows = self.env.cr.fetchall()

        labels = []
        values = []

        for row in rows:
            labels.append(row[0])
            values.append(row[1])

        return {
            'labels': labels,
            'values': values,
        }

    @api.model
    def get_top_deals(self, limit=10):
        """Top Deals by expeted revenue"""
        leads = self.search([
            ('type', '=', 'opportunity'),
            ('is_lost', '=', False),
            ('active', '=', True),
        ], order='expected_revenue desc', limit=limit)

        return [
            {
                'name': lead.name,
                'amount': lead.expected_revenue,
                'stage': lead.stage_id.name,
            }
            for lead in leads
        ]
        
    @api.model
    def get_lead_month_pie(self, kwargs):
        """pie chart"""
        month_count = []
        month_value = []
        leads = self.env['crm.lead'].search([])
        for rec in leads:
            month = rec.create_date.month
            if month not in month_value:
                month_value.append(month)
            month_count.append(month)
        month_val = [{'label': calendar.month_name[month],
                      'value': month_count.count(month)} for month in
                     month_value]
        names = [record['label'] for record in month_val]
        counts = [record['value'] for record in month_val]
        month = [counts, names]
        return month

    @api.model
    def get_the_sales_activity(self, kwargs):
        """Sales Activity Pie"""
        self._cr.execute('''SELECT mail_activity_type.name, COUNT(*) FROM 
                            mail_activity 
                            INNER JOIN mail_activity_type ON 
                            mail_activity.activity_type_id = mail_activity_type.id
                            WHERE mail_activity.res_model = 'crm.lead' 
                            GROUP BY mail_activity_type.name''')
        data = self._cr.dictfetchall()
        names = [record['name']['en_US'] for record in data]
        counts = [record['count'] for record in data]
        return [counts, names]

    @api.model
    def get_the_annual_target(self, kwargs):
        """Annual Target: Year To Date Graph"""
        session_user_id = self.env.uid
        self._cr.execute('''SELECT res_users.id, res_users.sales, res_users.sale_team_id, 
                                (SELECT crm_team.invoiced_target FROM crm_team 
                                WHERE crm_team.id = res_users.sale_team_id) as invoiced_target 
                                FROM res_users WHERE res_users.sales IS NOT NULL 
                                AND res_users.id=%s AND res_users.sale_team_id IS NOT NULL;''' % session_user_id)
        data2 = self._cr.dictfetchall()
        sales = [rec['sales'] for rec in data2]
        inv_target = [
            rec['invoiced_target'] if rec['invoiced_target'] is not None else 0
            for rec in data2]
        team_id = data2[-1]['sale_team_id'] if data2 else 0
        target_annual = sum(sales) + sum(inv_target)
        if self.env.user.has_group('sales_team.group_sale_manager'):
            self._cr.execute('''SELECT res_users.id,res_users.sales,
            res_users.sale_team_id, (SELECT crm_team.invoiced_target FROM 
            crm_team WHERE crm_team.id = res_users.sale_team_id) FROM res_users 
            WHERE res_users.id = %s AND res_users.sales is not null;'''
                             % session_user_id)
            data3 = self._cr.dictfetchall()
            sales = []
            inv_target = []
            for rec in data3:
                sales.append(rec['sales'])
                inv_target.append(rec['invoiced_target'])
                if inv_target == [None]:
                    inv_target = [0]
            ytd_target = (sum(sales) + sum(inv_target))
            self._cr.execute('''select sum(expected_revenue) from crm_lead 
            where stage_id=4 and team_id=%s AND Extract(Year FROM date_closed)=
            Extract(Year FROM DATE(NOW()))''' % team_id)
            achieved_won_data = self._cr.dictfetchall()
            achieved_won = [item['sum'] for item in achieved_won_data]
        else:
            self._cr.execute(
                '''SELECT res_users.id,res_users.sales FROM res_users WHERE 
                res_users.id = %s AND res_users.sales is not null;''' %
                session_user_id)
            data4 = self._cr.dictfetchall()
            sales = []
            for rec in data4:
                sales.append(rec['sales'])
            ytd_target = (sum(sales))
            self._cr.execute('''select sum(expected_revenue) from crm_lead 
            where stage_id=4 and user_id=%s AND 
            Extract(Year FROM date_closed)=Extract(Year FROM DATE(NOW()))'''
                             % session_user_id)
            achieved_won_data = self._cr.dictfetchall()
            achieved_won = [item['sum'] for item in achieved_won_data]
        won = achieved_won[0]
        if won is None:
            won = 0
        value = [target_annual, ytd_target, won]
        name = ["Annual Target", "YtD target", "Won"]
        final = [value, name]
        return final

    @api.model
    def get_the_campaign_pie(self, kwargs):
        """Leads Group By Campaign Pie"""
        self._cr.execute('''SELECT campaign_id, COUNT(*),
                            (SELECT name FROM utm_campaign 
                             WHERE utm_campaign.id = crm_lead.campaign_id)
                            FROM crm_lead WHERE campaign_id IS NOT NULL GROUP BY
                             campaign_id''')
        data = self._cr.dictfetchall()
        names = [record.get('name') for record in data]
        counts = [record.get('count') for record in data]
        final = [counts, names]
        return final

    @api.model
    def get_the_source_pie(self, kwargs):
        """Leads Group By Source Pie"""
        self._cr.execute('''SELECT source_id, COUNT(*),
                            (SELECT name FROM utm_source 
                             WHERE utm_source.id = crm_lead.source_id)
                            FROM crm_lead WHERE source_id IS NOT NULL GROUP BY 
                            source_id''')
        data = self._cr.dictfetchall()
        names = [record.get('name') for record in data]
        counts = [record.get('count') for record in data]
        final = [counts, names]
        return final

    @api.model
    def get_the_medium_pie(self, kwargs):
        """Leads Group By Medium Pie"""
        self._cr.execute('''SELECT medium_id, COUNT(*),
                            (SELECT name FROM utm_medium 
                             WHERE utm_medium.id = crm_lead.medium_id)
                            FROM crm_lead WHERE medium_id IS NOT NULL GROUP BY medium_id''')
        data = self._cr.dictfetchall()
        names = [record.get('name') for record in data]
        counts = [record.get('count') for record in data]
        final = [counts, names]
        return final

    @api.model
    def revenue_count_pie(self, kwargs):
        """Total expected revenue and count Pie"""
        session_user_id = self.env.uid

        def fetch_total_revenue(query):
            self._cr.execute(query)
            total_rev_data = self._cr.dictfetchall()
            total_rev = total_rev_data[0]['revenue'] if total_rev_data and \
                                                        total_rev_data[0][
                                                            'revenue'] else 0
            return total_rev

        queries = [
            f"SELECT sum(expected_revenue) as revenue FROM crm_lead WHERE user_id={session_user_id} AND type='opportunity' AND active='true'",
            f"SELECT sum(expected_revenue) as revenue FROM crm_lead WHERE user_id={session_user_id} AND type='opportunity' AND active='false' AND stage_id='4'",
            f"SELECT sum(expected_revenue) as revenue FROM crm_lead WHERE user_id={session_user_id} AND type='opportunity' AND active='false' AND probability='0' AND active='false'"
        ]
        total_expected_revenue, total_won_rev, total_lost_rev = [
            fetch_total_revenue(query) for query in queries]
        exp_revenue_without_won = total_expected_revenue - total_won_rev
        revenue_pie_count = [exp_revenue_without_won, total_won_rev,
                             total_lost_rev]
        revenue_pie_title = ['Expected without Won', 'Won', 'Lost']
        revenue_data = [revenue_pie_count, revenue_pie_title]
        return revenue_data

    @api.model
    def get_upcoming_events(self, kwargs):
        """Upcoming Activities Table"""
        today = fields.date.today()
        session_user_id = self.env.uid
        self._cr.execute('''select mail_activity.activity_type_id,
        mail_activity.date_deadline, mail_activity.summary,
        mail_activity.res_name,(SELECT mail_activity_type.name
        FROM mail_activity_type WHERE mail_activity_type.id = 
        mail_activity.activity_type_id), mail_activity.user_id FROM 
        mail_activity WHERE res_model = 'crm.lead' AND 
        mail_activity.date_deadline >= '%s' and user_id = %s GROUP BY 
        mail_activity.activity_type_id, mail_activity.date_deadline,
        mail_activity.summary,mail_activity.res_name,mail_activity.user_id
        order by mail_activity.date_deadline asc''' % (today, session_user_id))
        data = self._cr.fetchall()
        events = [[record[0], record[1], record[2], record[3],
                   record[4] if record[4] else '',
                   self.env['res.users'].browse(record[5]).name if record[
                       5] else ''
                   ] for record in data]
        return {
            'event': events,
            'cur_lang': self.env.context.get('lang')
        }

    @api.model
    def get_top_deals(self, kwargs):
        """Top 10 Deals Table"""
        self._cr.execute('''SELECT crm_lead.user_id,crm_lead.id,
        crm_lead.expected_revenue, crm_lead.name,crm_lead.company_id, 
        (SELECT crm_team.name FROM crm_team
        WHERE crm_lead.team_id = crm_team.id) from crm_lead where 
        crm_lead.expected_revenue is not null and crm_lead.type = 'opportunity' 
        GROUP BY crm_lead.user_id,
        crm_lead.id,crm_lead.expected_revenue,crm_lead.name,crm_lead.company_id
        order by crm_lead.expected_revenue DESC limit 10''')
        data1 = self._cr.fetchall()
        deals = [[self.env['res.users'].browse(rec[0]).name,
                  rec[1], rec[2], rec[3],
                  self.env['res.company'].browse(rec[4]).currency_id.symbol,
                  rec[5], index + 1] for index, rec in enumerate(data1)]
        return {'deals': deals}

    @api.model
    def get_monthly_goal(self, kwargs):
        """Monthly Goal Gauge"""
        uid = request.session.uid
        leads = self.env['crm.lead'].search([
            ('date_deadline', '!=', False), ('user_id', '=', uid),
            ('type', '=', 'opportunity')])
        leads_won = self.env['crm.lead'].search([
            ('date_closed', '!=', False), ('stage_id', '=', 4),
            ('user_id', '=', uid), ('type', '=', 'opportunity')])
        currency_symbol = self.env.company.currency_id.symbol
        achievement = sum(won.expected_revenue for won in leads_won.filtered(
            lambda a: a.date_closed.month == fields.date.today().month and
                      a.date_closed.year == fields.date.today().year))
        total = sum(rec.expected_revenue for rec in leads.filtered(
            lambda t: t.date_deadline.month == fields.date.today().month and
                      t.date_deadline.year == fields.date.today().year))
        self.monthly_goal = total
        self.achievement_amount = achievement
        percent = (achievement * 100 / total) / 100 if total > 0 else 0
        goals = [achievement, total, currency_symbol, percent]
        return {'goals': goals}

    @api.model
    def get_top_sp_revenue(self, kwargs):
        """Top 10 Salesperson revenue Table"""
        user = self.env.user
        self._cr.execute('''SELECT user_id, id, expected_revenue, name, company_id
                            FROM crm_lead 
                            WHERE expected_revenue IS NOT NULL AND user_id = %s
                            GROUP BY user_id, id 
                            ORDER BY expected_revenue DESC 
                            LIMIT 10''' % user.id)
        data1 = self._cr.fetchall()
        top_revenue = [
            [self.env['res.users'].browse(rec[0]).name, rec[1], rec[2],
             rec[3], self.env['res.company'].browse(rec[4]).currency_id.symbol]
            for rec in data1]
        return {'top_revenue': top_revenue}

    @api.model
    def get_country_revenue(self, kwargs):
        """Top 10 Country Wise Revenue - Heat Map"""
        company_id = self.env.company.id
        self._cr.execute('''SELECT country_id, sum(expected_revenue)
                            FROM crm_lead 
                            WHERE expected_revenue IS NOT NULL 
                            AND country_id IS NOT NULL
                            GROUP BY country_id 
                            ORDER BY sum(expected_revenue) DESC 
                            LIMIT 10''')
        data1 = self._cr.fetchall()
        country_revenue = [[self.env['res.country'].browse(rec[0]).name,
                            rec[1], self.env['res.company'].browse(
                company_id).currency_id.symbol] for rec in data1]
        return {'country_revenue': country_revenue}

    @api.model
    def get_country_count(self, kwargs):
        """Top 10 Country Wise Count - Heat Map"""
        self._cr.execute('''SELECT country_id, COUNT(*) 
                            FROM crm_lead 
                            WHERE country_id IS NOT NULL 
                            GROUP BY country_id 
                            ORDER BY COUNT(*) DESC 
                            LIMIT 10''')
        data1 = self._cr.fetchall()
        country_count = [[self.env['res.country'].browse(rec[0]).name, rec[1]]
                         for rec in data1]
        return {'country_count': country_count}

    @api.model
    def get_total_lost_crm(self, option):
        """Lost Opportunity or Lead Graph"""
        month_dict = {}
        for i in range(int(option) - 1, -1, -1):
            last_month = fields.Datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B')
            month_dict[text] = 0
        if option == '1':
            day_dict = {}
            last_day = date_utils.end_of(fields.Date.today(),
                                         "month").strftime("%d")
            for i in range(1, int(last_day), 1):
                day_dict[i] = 0
            self._cr.execute('''select create_date::date,count(id) from crm_lead
            where probability=0 and active=false and create_date between 
            (now() - interval '1 month') and now()
            group by create_date order by create_date;''')
            data = self._cr.dictfetchall()
            for rec in data:
                day_dict[int(rec['create_date'].strftime("%d"))] = rec['count']

            test = {'month': list(day_dict.keys()),
                    'count': list(day_dict.values())}
        else:
            month_string = str(int(option)) + ' Months'
            self._cr.execute('''select extract(month from create_date),count(id)
            from crm_lead where probability=0 and active=false and
            create_date between (now() - interval '%s') and now()
            group by extract(month from create_date) order by extract(
            month from create_date);''' % month_string)
            data = self._cr.dictfetchall()
            print("data", data)
            for rec in data:
                print("RECCCCCCC", rec)
                if rec.get("date_part"):
                    datetime_object = datetime.strptime(
                        str(int(rec['date_part'])), "%m")
                    month_name = datetime_object.strftime("%B")
                    month_dict[month_name] = rec['count']
            test = {'month': list(month_dict.keys()),
                    'count': list(month_dict.values())}
        return test

    @api.model
    def get_priority_distribution(self, kwargs=None):
        """Get count and percentage of each priority level (low, middle, high)."""
        priorities = ['low', 'middle', 'high']
        counts = {}

        # Hitung jumlah masing-masing priority
        for level in priorities:
            count = self.search_count([('priority_level', '=', level)])
            counts[level] = count

        total = sum(counts.values())
        percentages = {
            level: round((counts[level] / total * 100), 2) if total else 0
            for level in priorities
        }

        # Debug ke log Odoo
        print("=== PRIORITY DATA DEBUG ===")
        print("Counts:", counts)
        print("Percentages:", percentages)
        print("===========================")

        return {
            'counts': counts,
            'percentages': percentages,
            'total': total,
        }


    @api.model
    def get_ratio_based_country(self, kwargs):
        """Top 5 Won vs Lost Ratio based on Country"""
        self._cr.execute('''SELECT (SELECT name FROM res_country WHERE id=country_id),
                            COUNT(country_id)FROM crm_lead
                            WHERE probability=100 AND active=true
                            GROUP BY country_id
                            ORDER BY COUNT(country_id) DESC''')
        data_won = self._cr.fetchall()
        self._cr.execute('''SELECT (SELECT name FROM res_country WHERE id=country_id),
                                COUNT(country_id)
                            FROM crm_lead
                            WHERE probability=0 AND active=false
                            GROUP BY country_id
                            ORDER BY COUNT(country_id) DESC''')
        data_lost = self._cr.fetchall()
        country_wise_ratio = [[won[0], won[1], str(round(won[1] / next(
            (lost[1] for lost in data_lost if
             lost[0] == won[0] and lost[0] != 0 and won[1] != 0), 1),
                                                         2))] for won in
                              data_won[:5]]
        return {'country_wise_ratio': country_wise_ratio}

    @api.model
    def get_ratio_based_sp(self, kwargs):
        """Top 5 Won vs Lost Ratio based on Sales Person"""
        self._cr.execute('''select user_id,count(user_id) from crm_lead where
        probability=100 and active=true group by user_id order by 
        count(user_id) desc''')
        data_won = self._cr.fetchall()
        self._cr.execute('''select user_id,count(user_id) from crm_lead where 
        probability=0 and active=false group by user_id order by 
        count(user_id) desc''')
        data_lost = self._cr.fetchall()
        won = [[user_id_obj.name, rec[1]] for rec in data_won for user_id_obj in
               self.env['res.users'].browse(rec[0])]
        for won_list in won:
            won_list.append(next((lose[1] for lose in data_lost if
                                  self.env['res.users'].browse(
                                      data_won[won.index(won_list)][0]).name ==
                                  self.env['res.users'].browse(lose[0]).name),
                                 0))
        salesperson_wise_ratio = [[data[0], data[1], data[2],
                                   round(data[1] / data[2], 2) if data[
                                                                      2] != 0 else 0]
                                  for data in won if len(data) == 2]
        salesperson_wise_ratio = sorted(salesperson_wise_ratio,
                                        key=lambda x: x[3], reverse=True)[:5]
        return {'salesperson_wise_ratio': salesperson_wise_ratio}

    @api.model
    def get_ratio_based_sales_team(self, kwargs):
        """Top 5 Won vs Lost Ratio based on Sales Team"""
        self._cr.execute('''select (SELECT name FROM crm_team WHERE crm_team.id 
        = team_id), count(user_id) from crm_lead where probability=100 and 
        active=true group by team_id order by count(team_id) desc''')
        data_won = self._cr.fetchall()
        self._cr.execute('''select (SELECT name FROM crm_team WHERE crm_team.id 
        = team_id), count(user_id) from crm_lead where probability=0 and 
        active=false group by team_id order by count(team_id) desc''')
        data_lost = self._cr.fetchall()
        won = [[rec[0], rec[1]] for rec in data_won]
        for won_list in won:
            won_list.append(
                next((lose[1] for lose in data_lost if lose[0] == won_list[0]),
                     0))
        sales_team_wise_ratio = [[data[0], data[1], data[2],
                                  round(data[1] / data[2], 2) if data[
                                                                     2] != 0 else 0]
                                 for data in won if len(data) == 3]
        sales_team_wise_ratio = sorted(sales_team_wise_ratio,
                                       key=lambda x: x[3], reverse=True)[:5]
        return {'sales_team_wise_ratio': sales_team_wise_ratio}

    @api.model
    def get_lost_lead_by_reason_pie(self, kwargs):
        """Lost Leads by Lost Reason Pie"""
        self._cr.execute('''select lost_reason_id, count(*), (SELECT name FROM 
        crm_lost_reason WHERE id = lost_reason_id) from crm_lead where 
        probability=0 and active=false and type='lead' group by lost_reason_id''')
        data1 = self._cr.dictfetchall()
        name = [rec["name"] if rec["name"] is not None else "Undefined" for rec
                in data1]
        count = [rec["count"] for rec in data1]
        lost_leads = [count, name]
        return lost_leads

    @api.model
    def get_lost_lead_by_stage_pie(self, kwargs):
        """Lost Leads by Stage Pie"""
        self._cr.execute('''select stage_id, count(*),(SELECT name FROM 
        crm_stage WHERE id = stage_id) from crm_lead where probability=0 and 
        active=false and type='lead' group by stage_id''')
        data1 = self._cr.dictfetchall()
        name = [rec["name"] for rec in data1]
        count = [rec["count"] for rec in data1]
        lost_leads_stage = [count, name]
        return lost_leads_stage

    @api.model
    def get_recent_activities(self, kwargs):
        """Recent Activities Table"""
        today = fields.date.today()
        recent_week = today - relativedelta(days=7)
        self._cr.execute('''select mail_activity.activity_type_id,
        mail_activity.date_deadline, mail_activity.summary,
        mail_activity.res_name,(SELECT mail_activity_type.name
        FROM mail_activity_type WHERE mail_activity_type.id = 
        mail_activity.activity_type_id), mail_activity.user_id FROM 
        mail_activity WHERE res_model = 'crm.lead' AND
        mail_activity.date_deadline between '%s' and '%s' GROUP BY 
        mail_activity.activity_type_id, mail_activity.date_deadline,
        mail_activity.summary,mail_activity.res_name,mail_activity.user_id
        order by mail_activity.date_deadline desc''' % (recent_week, today))
        data = self._cr.fetchall()
        activities = [[*record[:5], self.env['res.users'].browse(record[5]).name
                       ] for record in data]
        return {'activities': activities}

    @api.model
    def get_count_unassigned(self, kwargs):
        """Unassigned Leads Count Card"""
        count_unassigned = self.env['crm.lead'].search_count(
            [('user_id', '=', False), ('type', '=', 'lead')])
        return {'count_unassigned': count_unassigned}

    @api.model
    def get_top_sp_by_invoice(self, kwargs=None):
        """
        Top N Sales Person by Invoice (Final, robust)
        Returns {'sales_person_invoice': [[name, total, currency_symbol, rank], ...]}
        Optional kwargs: {'limit': <int>}
        Notes:
         - Do NOT filter by res_users.active (we want to show non-active users too)
         - Use res_partner.name as primary display name, fallback to res_users.login
        """
        if kwargs is None:
            kwargs = {}

        try:
            limit = int(kwargs.get('limit', 10))
        except Exception:
            limit = 10

        # Query: aggregate invoice totals by the `invoice_user_id` relation.
        # Use LEFT JOINs so we still count invoices even if user/partner data incomplete.
        query = """
            SELECT
                COALESCE(rp.name, ru.login, 'Unassigned') AS salesperson,
                COALESCE(SUM(am.amount_total), 0) AS total,
                COALESCE(ru.company_id, %s) AS company_id
            FROM account_move am
            LEFT JOIN res_users ru ON am.invoice_user_id = ru.id
            LEFT JOIN res_partner rp ON ru.partner_id = rp.id
            WHERE am.move_type = 'out_invoice'
              AND am.state = 'posted'
            GROUP BY rp.name, ru.login, ru.company_id
            ORDER BY total DESC
            LIMIT %s
        """

        # Execute and fetch
        self._cr.execute(query, (self.env.company.id, limit))
        rows = self._cr.fetchall()

        sales_person_invoice = []
        company_cache = {}

        for idx, row in enumerate(rows):
            salesperson = row[0] or 'Unknown'
            total = float(row[1] or 0.0)
            company_id = row[2] or self.env.company.id

            # cache currency symbol per company
            if company_id in company_cache:
                currency_symbol = company_cache[company_id]
            else:
                comp = self.env['res.company'].browse(company_id)
                currency_symbol = (
                    comp.currency_id.symbol
                    if comp and comp.currency_id
                    else self.env.company.currency_id.symbol
                )
                company_cache[company_id] = currency_symbol

            sales_person_invoice.append([salesperson, total, currency_symbol, idx + 1])

        return {'sales_person_invoice': sales_person_invoice}

    @api.model
    def lead_details_user(self, kwargs):
        """Cards Count and Detail based on User"""
        session_user_id = self.env.uid
        month_count = []
        month_value = []
        leads = self.env['crm.lead'].search([])
        for rec in leads:
            month = rec.create_date.month
            if month not in month_value:
                month_value.append(month)
            month_count.append(month)
        value = []
        for index in range(len(month_value)):
            value = month_count.count(month_value[index])
        self._cr.execute('''SELECT res_users.id,res_users.sales,
        res_users.sale_team_id,(SELECT crm_team.invoiced_target FROM crm_team 
        WHERE crm_team.id = res_users.sale_team_id)
        FROM res_users WHERE res_users.sales is not null and res_users.id=%s
        AND res_users.sale_team_id is not null;''' % session_user_id)
        data2 = self._cr.dictfetchall()
        sales = []
        inv_target = []
        team_id = 0
        for rec in data2:
            sales.append(rec['sales'])
            inv_target.append(rec['invoiced_target'])
            if inv_target == [None]:
                inv_target = [0]
            team_id = rec['sale_team_id']
        target_annual = (sum(sales) + sum(inv_target))
        if self.env.user.has_group('sales_team.group_sale_manager'):
            self._cr.execute('''SELECT res_users.id,res_users.sales,
            res_users.sale_team_id,(SELECT crm_team.invoiced_target FROM 
            crm_team WHERE crm_team.id = res_users.sale_team_id) FROM 
            res_users WHERE res_users.id = %s AND res_users.sales is not 
            null;''' % session_user_id)
            data3 = self._cr.dictfetchall()
            sales = []
            inv_target = []
            for rec in data3:
                sales.append(rec['sales'])
                inv_target.append(rec['invoiced_target'])
                if inv_target == [None]:
                    inv_target = [0]
            ytd_target = (sum(sales) + sum(inv_target))
            self._cr.execute('''select sum(expected_revenue) from crm_lead where
             stage_id=4 and team_id=%s AND Extract(Year FROM date_closed)=
             Extract(Year FROM DATE(NOW()))''' % team_id)
            achieved_won_data = self._cr.dictfetchall()
            achieved_won = [item['sum'] for item in achieved_won_data]
        else:
            self._cr.execute('''SELECT res_users.id,res_users.sales FROM 
            res_users WHERE res_users.id = %s AND res_users.sales is not null;
            ''' % session_user_id)
            data4 = self._cr.dictfetchall()
            sales = []
            for rec in data4:
                sales.append(rec['sales'])
            ytd_target = (sum(sales))
            self._cr.execute('''select sum(expected_revenue) from crm_lead where
             stage_id=4 and user_id=%s AND Extract(Year FROM date_closed)=
             Extract(Year FROM DATE(NOW()))''' % session_user_id)
            achieved_won_data = self._cr.dictfetchall()
            achieved_won = [item['sum'] for item in achieved_won_data]
        won = achieved_won[0]
        if won is None:
            won = 0
        difference = target_annual - won
        self._cr.execute('''select COUNT(id) from crm_lead WHERE 
        crm_lead.user_id = '%s' AND Extract(MONTH FROM crm_lead.date_deadline) 
        = Extract( MONTH FROM DATE(NOW())) AND Extract(Year FROM 
        crm_lead.date_deadline) = Extract(Year FROM DATE(NOW()))
        ''' % session_user_id)
        record = self._cr.dictfetchall()
        rec_ids = [item['count'] for item in record]
        crm_lead_value = rec_ids[0]
        self._cr.execute('''select COUNT(id) from crm_lead WHERE 
        crm_lead.user_id = %s AND crm_lead.type = 'opportunity' AND 
        Extract(MONTH FROM crm_lead.date_deadline) = Extract(MONTH FROM 
        DATE(NOW())) AND Extract(Year FROM crm_lead.date_deadline
        ) = Extract(Year FROM DATE(NOW( )))''' % session_user_id)
        opportunity_data = self._cr.dictfetchall()
        opportunity_data_value = [item['count'] for item in opportunity_data]
        opportunity_value = opportunity_data_value[0]
        self._cr.execute('''select SUM(crm_lead.expected_revenue) from crm_lead 
        WHERE crm_lead.user_id = %s and type='opportunity' and active='true' 
        AND Extract(MONTH FROM crm_lead.date_deadline) = 
        Extract(MONTH FROM DATE(NOW())) AND Extract(Year FROM 
        crm_lead.date_deadline) = Extract(Year FROM DATE(NOW()))'''
                         % session_user_id)
        exp_revenue_data = self._cr.dictfetchall()
        exp_revenue_data_value = [item['sum'] for item in exp_revenue_data]
        exp_revenue_value = exp_revenue_data_value[0]
        if exp_revenue_value is None:
            exp_revenue_value = 0
        self._cr.execute('''select SUM(crm_lead.expected_revenue) from crm_lead 
        WHERE crm_lead.user_id = %s and type='opportunity' and active='true' 
        and stage_id=4 AND Extract(MONTH FROM crm_lead.date_closed) = 
        Extract(MONTH FROM DATE(NOW())) AND Extract(Year FROM 
        crm_lead.date_closed) = Extract(Year FROM DATE(NOW()))
        ''' % session_user_id)
        revenue_data = self._cr.dictfetchall()
        revenue_data_value = [item['sum'] for item in revenue_data]
        revenue_value = revenue_data_value[0]
        if revenue_value is None:
            revenue_value = 0
        ratio_value = []
        if revenue_value == 0:
            ratio_value = 0
        if revenue_value > 0:
            self._cr.execute('''select case when b.count_two = 0 then 0 else (
            CAST(a.count_one as float) / CAST(b.count_two as float))end as 
            final_count from (select COUNT(id) as count_one from crm_lead WHERE
            crm_lead.user_id = '%s' AND crm_lead.active = True AND 
            crm_lead.probability = 100 AND Extract(MONTH FROM 
            crm_lead.date_deadline) = Extract(MONTH FROM DATE(NOW()))
            AND Extract(Year FROM crm_lead.date_open) = Extract(Year 
            FROM DATE(NOW())))a,(select COUNT(id) as count_two from crm_lead 
            WHERE crm_lead.user_id = '%s' AND crm_lead.active = False AND 
            crm_lead.probability = 0 AND Extract(MONTH FROM 
            crm_lead.date_deadline) = Extract(MONTH FROM DATE(NOW())) AND 
            Extract(Year FROM crm_lead.date_deadline) = Extract(Year FROM 
            DATE(NOW())))b''' % (session_user_id, session_user_id))
            ratio_data_value = [row[0] for row in self._cr.fetchall()]
            ratio_value = str(ratio_data_value)[1:-1]
        self._cr.execute('''SELECT active,count(active) FROM crm_lead where 
        type='opportunity' and active = true and probability = 100 and 
        user_id=%s AND Extract(MONTH FROM date_closed) = Extract(MONTH FROM 
        DATE(NOW())) AND Extract(Year FROM date_closed) = Extract(
        Year FROM DATE(NOW())) or type='opportunity' and active = false and 
        probability = 0 and user_id=%s AND Extract(MONTH FROM date_deadline) = 
        Extract(MONTH FROM DATE(NOW())) AND Extract(Year FROM date_deadline) = 
        Extract(Year FROM DATE(NOW())) GROUP BY active
        ''' % (session_user_id, session_user_id))
        record_opportunity = dict(self._cr.fetchall())
        opportunity_ratio_value = 0.0
        if record_opportunity == {}:
            opportunity_ratio_value = 0.0
        else:
            total_opportunity_won = record_opportunity.get(False)
            total_opportunity_lost = record_opportunity.get(True)
            if total_opportunity_won is None:
                total_opportunity_won = 0
            if total_opportunity_lost is None:
                total_opportunity_lost = 0
                opportunity_ratio_value = 0.0
            if total_opportunity_lost > 0:
                opportunity_ratio_value = round(
                    total_opportunity_won / total_opportunity_lost, 2)
        avg = 0
        if crm_lead_value == 1:
            self._cr.execute('''SELECT id, date_conversion, create_date
            FROM crm_lead WHERE date_conversion IS NOT NULL;''')
            data = self._cr.dictfetchall()
            for rec in data:
                date_close = rec['date_conversion']
                date_create = rec['create_date']
                avg = (date_close - date_create).seconds
        if crm_lead_value > 1:
            self._cr.execute('''SELECT id, date_conversion, create_date
            FROM crm_lead WHERE date_conversion IS NOT NULL;''')
            data1 = self._cr.dictfetchall()
            for rec in data1:
                date_close = rec['date_conversion']
                date_create = rec['create_date']
                avg = (date_close - date_create).seconds
        avg_time = 0 if crm_lead_value == 0 else round(avg / crm_lead_value)
        data = {
            'record': crm_lead_value,
            'record_op': opportunity_value,
            'record_rev_exp': exp_revenue_value,
            'record_rev': revenue_value,
            'record_ratio': ratio_value,
            'opportunity_ratio_value': str(opportunity_ratio_value),
            'avg_time': avg_time,
            'count': value,
            'target': target_annual,
            'ytd_target': ytd_target,
            'difference': difference,
            'won': won,
        }
        return data

    @api.model
    def crm_year(self, kwargs):
        """Yearly CRM KPIs (robust) with corrected win/lost ratio (Option A)."""

        # normalize rpc arg shapes
        if isinstance(kwargs, (list, tuple)) and len(kwargs) and isinstance(kwargs[0], dict):
            kwargs = kwargs[0]
        kwargs = kwargs or {}

        session_user = self.env.user
        session_user_id = session_user.id
        by_all = bool(kwargs.get('by_all', False))

        user_filter = "" if by_all else f"AND user_id = {session_user_id}"

        # helper to convert ids to SQL tuple
        def _sql_tuple(ids):
            if not ids:
                return "(0)"
            try:
                ids_list = [int(i) for i in ids]
            except Exception:
                try:
                    return f"({int(ids)})"
                except Exception:
                    return "(0)"
            if len(ids_list) == 1:
                return f"({ids_list[0]})"
            return f"({','.join(str(i) for i in ids_list)})"

        # determine stage groups
        try:
            won_stage_ids = _sql_tuple(self.env['crm.stage'].search([('is_won', '=', True)]).ids)
            lost_stage_ids = _sql_tuple(self.env['crm.stage'].search([('fold', '=', True)]).ids)
        except Exception:
            won_stage_ids = "(0)"
            lost_stage_ids = "(0)"

        new_stage_id = 1

        # ----- Leads (year) -----
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE EXTRACT(YEAR FROM create_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            {user_filter}
        """)
        crm_lead_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # ----- Opportunities (year) -----
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE type = 'opportunity'
            AND EXTRACT(YEAR FROM create_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            {user_filter}
        """)
        opportunity_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # ----- Expected revenue (year) -----
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_rev
            FROM crm_lead
            WHERE type = 'opportunity' AND active = true
            AND EXTRACT(YEAR FROM create_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            {user_filter}
        """)
        exp_revenue_value = float((self._cr.dictfetchone() or {'total_rev': 0})['total_rev'])

        # ----- Won revenue (year) -----
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_won
            FROM crm_lead
            WHERE type='opportunity'
            AND stage_id IN {won_stage_ids}
            AND date_closed IS NOT NULL
            AND EXTRACT(YEAR FROM date_closed) = EXTRACT(YEAR FROM CURRENT_DATE)
            {user_filter}
        """)
        revenue_value = float((self._cr.dictfetchone() or {'total_won': 0})['total_won'])

        ratio_value = round((revenue_value / exp_revenue_value) * 100, 2) if exp_revenue_value else 0.0

        # ================================================================
        # ðŸ”¥ WIN & LOST RATIO (LOGIKA LAMA â€” option A)
        # ================================================================
        self._cr.execute(f"""
            SELECT
                SUM(
                    CASE WHEN probability = 100 AND active = true
                        AND EXTRACT(YEAR FROM date_closed) = EXTRACT(YEAR FROM CURRENT_DATE)
                    THEN 1 ELSE 0 END
                ) AS won_count,

                SUM(
                    CASE WHEN probability = 0 AND active = false
                        AND EXTRACT(YEAR FROM create_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                    THEN 1 ELSE 0 END
                ) AS lost_count
            FROM crm_lead
            WHERE type='opportunity'
            {user_filter}
        """)

        opp = self._cr.dictfetchone() or {}
        total_won = int(opp.get('won_count') or 0)
        total_lost = int(opp.get('lost_count') or 0)
        total_compared = total_won + total_lost

        win_ratio_value = round((total_won / total_compared) * 100, 2) if total_compared else 0.0
        lost_ratio_value = round((total_lost / total_compared) * 100, 2) if total_compared else 0.0

        # ----- Follow Up Do (year) -----
        try:
            self._cr.execute(f"""
                SELECT COUNT(id) AS cnt
                FROM crm_lead
                WHERE type='opportunity'
                AND active=true
                AND EXTRACT(YEAR FROM create_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                AND stage_id NOT IN ({new_stage_id})
                AND stage_id NOT IN {won_stage_ids}
                AND stage_id NOT IN {lost_stage_ids}
                {user_filter}
            """)
            follow_up_do = int((self._cr.dictfetchone() or {'cnt': 0})['cnt'])
        except Exception:
            follow_up_do = 0

        # ----- Avg close time (year) -----
        self._cr.execute(f"""
            SELECT AVG(EXTRACT(EPOCH FROM (date_conversion - create_date))) AS avg_sec
            FROM crm_lead
            WHERE date_conversion IS NOT NULL
            AND EXTRACT(YEAR FROM date_conversion) = EXTRACT(YEAR FROM CURRENT_DATE)
            {user_filter}
        """)
        avg_seconds = float((self._cr.dictfetchone() or {'avg_sec': 0})['avg_sec'] or 0)
        record_avg_time = int(round(avg_seconds)) if avg_seconds else 0

        # ================================================================
        # â­ EMAIL SENT (YEAR) â€” counting crm.lead with source 'Email Marketing'
        #    (using ORM search_count for robustness)
        # ================================================================
        try:
            start_of_year = date_utils.start_of(fields.Date.today(), 'year')
            end_of_year = date_utils.end_of(fields.Date.today(), 'year')
            email_sent_year = self.env['crm.lead'].search_count([
                ('source_id.name', '=', 'Email Marketing'),
                ('create_date', '>=', start_of_year),
                ('create_date', '<=', end_of_year),
            ])
        except Exception:
            # fallback: zero if anything goes wrong
            email_sent_year = 0

        return {
            'record': crm_lead_value,
            'record_op': opportunity_value,
            'record_rev_exp': exp_revenue_value,
            'record_rev': revenue_value,
            'record_ratio': ratio_value,
            'opportunity_ratio_value': win_ratio_value,
            'lost_ratio': lost_ratio_value,
            'avg_time': record_avg_time,
            'follow_up_do': follow_up_do,

            # ðŸ”¥ KPI BARU
            'email_sent_year': email_sent_year,
        }


    @api.model
    def crm_quarter(self, kwargs):
        """Quarterly CRM KPIs (corrected win/lost ratio â€“ Option A)."""

        if isinstance(kwargs, (list, tuple)) and len(kwargs) and isinstance(kwargs[0], dict):
            kwargs = kwargs[0]
        kwargs = kwargs or {}

        session_user = self.env.user
        session_user_id = session_user.id
        by_all = bool(kwargs.get('by_all', False))
        user_filter = "" if by_all else f"AND user_id = {session_user_id}"

        today = fields.Date.today()
        start_of_quarter = date_utils.start_of(today, 'quarter')
        end_of_quarter = date_utils.end_of(today, 'quarter')

        def _sql_tuple(ids):
            if not ids:
                return "(0)"
            try:
                ids_list = [int(i) for i in ids]
            except Exception:
                try:
                    return f"({int(ids)})"
                except Exception:
                    return "(0)"
            if len(ids_list) == 1:
                return f"({ids_list[0]})"
            return f"({','.join(str(i) for i in ids_list)})"

        try:
            won_stage_ids = _sql_tuple(self.env['crm.stage'].search([('is_won', '=', True)]).ids)
            lost_stage_ids = _sql_tuple(self.env['crm.stage'].search([('fold', '=', True)]).ids)
        except Exception:
            won_stage_ids = "(0)"
            lost_stage_ids = "(0)"

        new_stage_id = 1

        # Leads
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE create_date >= %s AND create_date <= %s
            {user_filter}
        """, (start_of_quarter, end_of_quarter))
        crm_lead_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # Opportunities
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE type='opportunity'
            AND create_date >= %s AND create_date <= %s
            {user_filter}
        """, (start_of_quarter, end_of_quarter))
        opportunity_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # Expected revenue
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_rev
            FROM crm_lead
            WHERE type='opportunity'
            AND active=true
            AND create_date >= %s AND create_date <= %s
            {user_filter}
        """, (start_of_quarter, end_of_quarter))
        exp_revenue_value = float((self._cr.dictfetchone() or {'total_rev': 0})['total_rev'])

        # Won revenue
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_won
            FROM crm_lead
            WHERE type='opportunity'
            AND stage_id IN {won_stage_ids}
            AND date_closed IS NOT NULL
            AND date_closed >= %s AND date_closed <= %s
            {user_filter}
        """, (start_of_quarter, end_of_quarter))
        revenue_value = float((self._cr.dictfetchone() or {'total_won': 0})['total_won'])

        ratio_value = round((revenue_value / exp_revenue_value) * 100, 2) if exp_revenue_value else 0.0

        # Win/lost ratio
        self._cr.execute(f"""
            SELECT
                SUM(CASE WHEN probability = 100 AND active = true
                            AND date_closed >= %s AND date_closed <= %s
                    THEN 1 ELSE 0 END) AS won_count,

                SUM(CASE WHEN probability = 0 AND active = false
                            AND create_date >= %s AND create_date <= %s
                    THEN 1 ELSE 0 END) AS lost_count

            FROM crm_lead
            WHERE type='opportunity'
            {user_filter}
        """, (start_of_quarter, end_of_quarter,
            start_of_quarter, end_of_quarter))

        opp = self._cr.dictfetchone() or {}
        total_won = int(opp.get('won_count') or 0)
        total_lost = int(opp.get('lost_count') or 0)
        total_compared = total_won + total_lost

        win_ratio_value = round((total_won / total_compared) * 100, 2) if total_compared else 0.0
        lost_ratio_value = round((total_lost / total_compared) * 100, 2) if total_compared else 0.0

        # ----- Follow Up DO (quarter) -----
        try:
            self._cr.execute(f"""
                SELECT COUNT(id) AS cnt
                FROM crm_lead
                WHERE type='opportunity'
                AND active=true
                AND create_date >= %s AND create_date <= %s
                AND stage_id NOT IN ({new_stage_id})
                AND stage_id NOT IN {won_stage_ids}
                AND stage_id NOT IN {lost_stage_ids}
                {user_filter}
            """, (start_of_quarter, end_of_quarter))
            follow_up_do = int((self._cr.dictfetchone() or {'cnt': 0})['cnt'])
        except Exception:
            follow_up_do = 0

        # Avg close time
        self._cr.execute(f"""
            SELECT AVG(EXTRACT(EPOCH FROM (date_conversion - create_date))) AS avg_sec
            FROM crm_lead
            WHERE date_conversion IS NOT NULL
            AND date_conversion >= %s AND date_conversion <= %s
            {user_filter}
        """, (start_of_quarter, end_of_quarter))
        avg_seconds = float((self._cr.dictfetchone() or {'avg_sec': 0})['avg_sec'] or 0)
        record_avg_time = int(round(avg_seconds)) if avg_seconds else 0

        # ================================================================
        # â­ EMAIL SENT (QUARTER) â€” counting crm.lead with source 'Email Marketing'
        # ================================================================
        try:
            email_sent_quarter = self.env['crm.lead'].search_count([
                ('source_id.name', '=', 'Email Marketing'),
                ('create_date', '>=', start_of_quarter),
                ('create_date', '<=', end_of_quarter),
            ])
        except Exception:
            email_sent_quarter = 0

        return {
            'record': crm_lead_value,
            'record_op': opportunity_value,
            'record_rev_exp': exp_revenue_value,
            'record_rev': revenue_value,
            'record_ratio': ratio_value,
            'opportunity_ratio_value': win_ratio_value,
            'lost_ratio': lost_ratio_value,
            'avg_time': record_avg_time,
            'follow_up_do': follow_up_do,

            # ðŸ”¥ KPI BARU
            'email_sent_quarter': email_sent_quarter,
        }


    @api.model
    def crm_month(self, kwargs):
        """Monthly CRM KPIs with corrected win/lost ratio (Option A)."""

        # normalize RPC arg shapes
        if isinstance(kwargs, (list, tuple)) and len(kwargs) and isinstance(kwargs[0], dict):
            kwargs = kwargs[0]
        kwargs = kwargs or {}

        session_user = self.env.user
        session_user_id = session_user.id
        by_all = bool(kwargs.get('by_all', False))
        user_filter = "" if by_all else f"AND user_id = {session_user_id}"

        # Helper: convert ids to SQL tuple
        def _sql_tuple(ids):
            if not ids:
                return "(0)"
            try:
                ids_list = [int(i) for i in ids]
            except Exception:
                try:
                    return f"({int(ids)})"
                except Exception:
                    return "(0)"
            if len(ids_list) == 1:
                return f"({ids_list[0]})"
            return f"({','.join(str(i) for i in ids_list)})"

        # Stage groups
        try:
            won_stage_ids = _sql_tuple(self.env['crm.stage'].search([('is_won', '=', True)]).ids)
            lost_stage_ids = _sql_tuple(self.env['crm.stage'].search([('fold', '=', True)]).ids)
        except Exception:
            won_stage_ids = "(0)"
            lost_stage_ids = "(0)"

        new_stage_id = 1  # default "New" stage id

        # Get month range
        today = fields.Date.today()
        start_of_month = date_utils.start_of(today, 'month')
        end_of_month = date_utils.end_of(today, 'month')

        # ----- Leads (month) -----
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE create_date >= %s AND create_date <= %s
            {user_filter}
        """, (start_of_month, end_of_month))
        crm_lead_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # ----- Opportunities (month) -----
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE type='opportunity'
            AND create_date >= %s AND create_date <= %s
            {user_filter}
        """, (start_of_month, end_of_month))
        opportunity_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # ----- Expected revenue (month) -----
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_rev
            FROM crm_lead
            WHERE type='opportunity'
            AND active=true
            AND create_date >= %s AND create_date <= %s
            {user_filter}
        """, (start_of_month, end_of_month))
        exp_revenue_value = float((self._cr.dictfetchone() or {'total_rev': 0})['total_rev'])

        # ----- Won revenue (month) -----
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_won
            FROM crm_lead
            WHERE type='opportunity'
            AND stage_id IN {won_stage_ids}
            AND date_closed IS NOT NULL
            AND date_closed >= %s AND date_closed <= %s
            {user_filter}
        """, (start_of_month, end_of_month))
        revenue_value = float((self._cr.dictfetchone() or {'total_won': 0})['total_won'])

        ratio_value = round((revenue_value / exp_revenue_value) * 100, 2) if exp_revenue_value else 0.0

        # ================================================================
        # ðŸ”¥ WIN & LOST RATIO â€” LOGIKA LAMA 100% ORIGINAL
        # ================================================================
        self._cr.execute(f"""
            SELECT
                SUM(
                    CASE WHEN probability = 100 AND active = true
                        AND date_closed >= %s AND date_closed <= %s
                    THEN 1 ELSE 0 END
                ) AS won_count,

                SUM(
                    CASE WHEN probability = 0 AND active = false
                        AND create_date >= %s AND create_date <= %s
                    THEN 1 ELSE 0 END
                ) AS lost_count

            FROM crm_lead
            WHERE type='opportunity'
            {user_filter}
        """, (start_of_month, end_of_month,
            start_of_month, end_of_month))

        opp = self._cr.dictfetchone() or {}
        total_won = int(opp.get('won_count') or 0)
        total_lost = int(opp.get('lost_count') or 0)
        total_compared = total_won + total_lost

        win_ratio_value = round((total_won / total_compared) * 100, 2) if total_compared else 0.0
        lost_ratio_value = round((total_lost / total_compared) * 100, 2) if total_compared else 0.0

        # ----- Follow Up DO (month) -----
        try:
            self._cr.execute(f"""
                SELECT COUNT(id) AS cnt
                FROM crm_lead
                WHERE type='opportunity'
                AND active=true
                AND create_date >= %s AND create_date <= %s
                AND stage_id NOT IN ({new_stage_id})
                AND stage_id NOT IN {won_stage_ids}
                AND stage_id NOT IN {lost_stage_ids}
                {user_filter}
            """, (start_of_month, end_of_month))
            follow_up_do = int((self._cr.dictfetchone() or {'cnt': 0})['cnt'])
        except Exception:
            follow_up_do = 0

        # ----- Avg close time (month) -----
        self._cr.execute(f"""
            SELECT AVG(EXTRACT(EPOCH FROM (date_conversion - create_date))) AS avg_sec
            FROM crm_lead
            WHERE date_conversion IS NOT NULL
            AND date_conversion >= %s AND date_conversion <= %s
            {user_filter}
        """, (start_of_month, end_of_month))
        avg_seconds = float((self._cr.dictfetchone() or {'avg_sec': 0})['avg_sec'] or 0)
        record_avg_time = int(round(avg_seconds)) if avg_seconds else 0

        # ================================================================
        # â­ EMAIL SENT (MONTH) â€” counting crm.lead with source 'Email Marketing'
        # ================================================================
        try:
            email_sent_month = self.env['crm.lead'].search_count([
                ('source_id.name', '=', 'Email Marketing'),
                ('create_date', '>=', start_of_month),
                ('create_date', '<=', end_of_month),
            ])
        except Exception:
            email_sent_month = 0

        return {
            'record': crm_lead_value,
            'record_op': opportunity_value,
            'record_rev_exp': exp_revenue_value,
            'record_rev': revenue_value,
            'record_ratio': ratio_value,
            'opportunity_ratio_value': win_ratio_value,
            'lost_ratio': lost_ratio_value,
            'avg_time': record_avg_time,
            'follow_up_do': follow_up_do,

            # ðŸ”¥ KPI BARU
            'email_sent_month': email_sent_month,
        }


    @api.model
    def crm_week(self, kwargs):
        """Weekly CRM KPIs with corrected win/lost ratio (Option A)."""

        # normalize rpc args
        if isinstance(kwargs, (list, tuple)) and len(kwargs) and isinstance(kwargs[0], dict):
            kwargs = kwargs[0]
        kwargs = kwargs or {}

        session_user = self.env.user
        session_user_id = session_user.id
        by_all = bool(kwargs.get('by_all', False))
        user_filter = "" if by_all else f"AND user_id = {session_user_id}"

        # Helper: build SQL tuple
        def _sql_tuple(ids):
            if not ids:
                return "(0)"
            try:
                ids_list = [int(i) for i in ids]
            except Exception:
                try:
                    return f"({int(ids)})"
                except Exception:
                    return "(0)"
            if len(ids_list) == 1:
                return f"({ids_list[0]})"
            return f"({','.join(str(i) for i in ids_list)})"

        # Stage groups
        try:
            won_stage_ids = _sql_tuple(self.env['crm.stage'].search([('is_won', '=', True)]).ids)
            lost_stage_ids = _sql_tuple(self.env['crm.stage'].search([('fold', '=', True)]).ids)
        except Exception:
            won_stage_ids = "(0)"
            lost_stage_ids = "(0)"

        new_stage_id = 1  # New stage

        # ===============================
        # RANGE MINGGU (Mondayâ€“Sunday)
        # ===============================
        today = fields.Date.today()
        weekday = today.weekday()  # Monday=0 ... Sunday=6
        start_of_week = today - timedelta(days=weekday)
        end_of_week = start_of_week + timedelta(days=6)

        # Convert ke datetime lengkap
        start_dt = datetime.combine(start_of_week, datetime.min.time())
        end_dt = datetime.combine(end_of_week, datetime.max.time())

        # ----- Leads (week) -----
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE create_date BETWEEN %s AND %s
            {user_filter}
        """, (start_dt, end_dt))
        crm_lead_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # ----- Opportunities (week) -----
        self._cr.execute(f"""
            SELECT COUNT(id) AS count
            FROM crm_lead
            WHERE type='opportunity'
            AND create_date BETWEEN %s AND %s
            {user_filter}
        """, (start_dt, end_dt))
        opportunity_value = int((self._cr.dictfetchone() or {'count': 0})['count'])

        # ----- Expected revenue (week) -----
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_rev
            FROM crm_lead
            WHERE type='opportunity'
            AND active=true
            AND create_date BETWEEN %s AND %s
            {user_filter}
        """, (start_dt, end_dt))
        exp_revenue_value = float((self._cr.dictfetchone() or {'total_rev': 0})['total_rev'])

        # ----- Won revenue (week) -----
        self._cr.execute(f"""
            SELECT COALESCE(SUM(expected_revenue), 0) AS total_won
            FROM crm_lead
            WHERE type='opportunity'
            AND stage_id IN {won_stage_ids}
            AND date_closed IS NOT NULL
            AND date_closed BETWEEN %s AND %s
            {user_filter}
        """, (start_dt, end_dt))
        revenue_value = float((self._cr.dictfetchone() or {'total_won': 0})['total_won'])

        ratio_value = round((revenue_value / exp_revenue_value) * 100, 2) if exp_revenue_value else 0.0

        # ================================================================
        # ðŸ”¥ WIN & LOST RATIO â€” LOGIKA LAMA 100% ORIGINAL
        # ================================================================
        self._cr.execute(f"""
            SELECT
                SUM(CASE
                        WHEN probability = 100
                        AND active = true
                        AND date_closed BETWEEN %s AND %s
                    THEN 1 ELSE 0 END) AS won_count,

                SUM(CASE
                        WHEN probability = 0
                        AND active = false
                        AND create_date BETWEEN %s AND %s
                    THEN 1 ELSE 0 END) AS lost_count

            FROM crm_lead
            WHERE type='opportunity'
            {user_filter}
        """, (start_dt, end_dt, start_dt, end_dt))

        opp = self._cr.dictfetchone() or {}
        total_won = int(opp.get('won_count') or 0)
        total_lost = int(opp.get('lost_count') or 0)
        total_compared = total_won + total_lost

        win_ratio_value = round((total_won / total_compared) * 100, 2) if total_compared else 0.0
        lost_ratio_value = round((total_lost / total_compared) * 100, 2) if total_compared else 0.0

        # ----- Follow Up DO (week) -----
        try:
            self._cr.execute(f"""
                SELECT COUNT(id) AS cnt
                FROM crm_lead
                WHERE type='opportunity'
                AND active=true
                AND create_date BETWEEN %s AND %s
                AND stage_id NOT IN ({new_stage_id})
                AND stage_id NOT IN {won_stage_ids}
                AND stage_id NOT IN {lost_stage_ids}
                {user_filter}
            """, (start_dt, end_dt))
            follow_up_do = int((self._cr.dictfetchone() or {'cnt': 0})['cnt'])
        except Exception:
            follow_up_do = 0

        # ----- Avg close time (week) -----
        self._cr.execute(f"""
            SELECT AVG(EXTRACT(EPOCH FROM (date_conversion - create_date))) AS avg_sec
            FROM crm_lead
            WHERE date_conversion IS NOT NULL
            AND date_conversion BETWEEN %s AND %s
            {user_filter}
        """, (start_dt, end_dt))

        avg_seconds = float((self._cr.dictfetchone() or {'avg_sec': 0})['avg_sec'] or 0)
        record_avg_time = int(round(avg_seconds)) if avg_seconds else 0

        # ================================================================
        # â­ EMAIL SENT (WEEK) â€” counting crm.lead with source 'Email Marketing'
        # ================================================================
        try:
            email_sent_week = self.env['crm.lead'].search_count([
                ('source_id.name', '=', 'Email Marketing'),
                ('create_date', '>=', start_dt),
                ('create_date', '<=', end_dt),
            ])
        except Exception:
            email_sent_week = 0

        return {
            'record': crm_lead_value,
            'record_op': opportunity_value,
            'record_rev_exp': exp_revenue_value,
            'record_rev': revenue_value,
            'record_ratio': ratio_value,
            'opportunity_ratio_value': win_ratio_value,
            'lost_ratio': lost_ratio_value,
            'avg_time': record_avg_time,
            'follow_up_do': follow_up_do,

            # ðŸ”¥ KPI BARU
            'email_sent_week': email_sent_week,
        }

