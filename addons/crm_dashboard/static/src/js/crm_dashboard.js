/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted } = owl;
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";

export class CRMDashboard extends Component {

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        // Pastikan event handler tetap ter-bind
        this.on_change_income_expense_values = this.on_change_income_expense_values.bind(this);

        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
    }

    async onWillStart() {
        var self = this;
        this.login_employee = {};

        var def0 = jsonrpc('/web/dataset/call_kw/crm.lead/check_user_group', {
            model: 'crm.lead',
            method: 'check_user_group',
            args: [{}],
            kwargs: {},
        }).then(function(result) {
            self.is_manager = !!result;
        });

        var def1 = jsonrpc('/web/dataset/call_kw/crm.lead/get_upcoming_events', {
            model: "crm.lead",
            method: "get_upcoming_events",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.upcoming_events = res['event'];
            self.current_lang = res['cur_lang'];
        });

        var def2 = jsonrpc('/web/dataset/call_kw/crm.lead/get_top_deals', {
            model: "crm.lead",
            method: "get_top_deals",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_deals = res['deals'];
        });

        var def3 = jsonrpc('/web/dataset/call_kw/crm.lead/get_monthly_goal', {
            model: "crm.lead",
            method: "get_monthly_goal",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.monthly_goals = res['goals'];
        });

        var def4 = jsonrpc('/web/dataset/call_kw/crm.lead/get_top_sp_revenue', {
            model: "crm.lead",
            method: "get_top_sp_revenue",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_sp_revenue = res['top_revenue'];
        });

        var def5 = jsonrpc('/web/dataset/call_kw/crm.lead/get_country_revenue', {
            model: "crm.lead",
            method: "get_country_revenue",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_country_revenue = res['country_revenue'];
        });

        var def6 = jsonrpc('/web/dataset/call_kw/crm.lead/get_country_count', {
            model: "crm.lead",
            method: "get_country_count",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_country_count = res['country_count'];
        });

        var def8 = jsonrpc('/web/dataset/call_kw/crm.lead/get_ratio_based_country', {
            model: "crm.lead",
            method: "get_ratio_based_country",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_country_wise_ratio = res['country_wise_ratio'];
        });

        var def9 = jsonrpc('/web/dataset/call_kw/crm.lead/get_ratio_based_sp', {
            model: "crm.lead",
            method: "get_ratio_based_sp",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_salesperson_wise_ratio = res['salesperson_wise_ratio'];
        });

        var def10 = jsonrpc('/web/dataset/call_kw/crm.lead/get_ratio_based_sales_team', {
            model: "crm.lead",
            method: "get_ratio_based_sales_team",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_sales_team_wise_ratio = res['sales_team_wise_ratio'];
        });

        var def11 = jsonrpc('/web/dataset/call_kw/crm.lead/get_recent_activities', {
            model: "crm.lead",
            method: "get_recent_activities",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.recent_activities = res['activities'];
        });

        var def12 = jsonrpc('/web/dataset/call_kw/crm.lead/get_count_unassigned', {
            model: "crm.lead",
            method: "get_count_unassigned",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.get_count_unassigned = res['count_unassigned'];
        });

        var def13 = jsonrpc('/web/dataset/call_kw/crm.lead/get_top_sp_by_invoice', {
            model: "crm.lead",
            method: "get_top_sp_by_invoice",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.top_sp_by_invoice = res['sales_person_invoice'];
        });

        var def14 = jsonrpc('/web/dataset/call_kw/crm.lead/get_active_leads', {
            model: "crm.lead",
            method: "get_active_leads",
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            self.active_leads_count = parseInt(res?.active_leads || 0, 10);
        }).catch(function(err) {
            console.error('Failed to load Active Leads:', err);
            self.active_leads_count = 0;
        });

        return $.when(def0, def1, def2, def3, def4, def5, def6,
                      def8, def9, def10, def11, def12, def13, def14);
    }

    /**
     * Hitung tanggal start & end sesuai periode
     */
    _getDateRange(period) {
        const now = new Date();
        let start, end;

        if (period === "this_week") {
            const day = now.getDay();
            const diff = now.getDate() - day + (day === 0 ? -6 : 1);
            start = new Date(now.setDate(diff));
            end = new Date();
        } else if (period === "this_month") {
            start = new Date(now.getFullYear(), now.getMonth(), 1);
            end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        } else if (period === "this_quarter") {
            const q = Math.floor(now.getMonth() / 3);
            start = new Date(now.getFullYear(), q * 3, 1);
            end = new Date(now.getFullYear(), q * 3 + 3, 0);
        } else if (period === "this_year") {
            start = new Date(now.getFullYear(), 0, 1);
            end = new Date(now.getFullYear(), 11, 31);
        } else {
            start = new Date(now.getFullYear(), 0, 1);
            end = new Date();
        }

        return {
            start: start.toISOString().split('T')[0],
            end: end.toISOString().split('T')[0],
        };
    }

    /**
     * Refresh Active Leads — bisa untuk periode tertentu
     */
    async refreshActiveLeads(period = null) {
        try {
            let args = [];
            if (period) {
                const { start, end } = this._getDateRange(period);
                args = [start, end];
            }

            const res = await jsonrpc('/web/dataset/call_kw/crm.lead/get_active_leads', {
                model: 'crm.lead',
                method: 'get_active_leads',
                args: args,
                kwargs: {},
            });

            const count = res && res.active_leads ? parseInt(res.active_leads, 10) : 0;
            const el = document.querySelector('#active_leads');
            if (el) el.innerHTML = count;
        } catch (err) {
            console.error('Failed to refresh Active Leads:', err);
        }
    }

    on_change_income_expense_values(e) {
        e.stopPropagation();
        var $target = $(e.target);
        var value = $target.val();
        if (value === "this_year") {
            this.onclick_this_year();
        } else if (value === "this_quarter") {
            this.onclick_this_quarter();
        } else if (value === "this_month") {
            this.onclick_this_month();
        } else if (value === "this_week") {
            this.onclick_this_week();
        }
    }

    onclick_this_week(ev) {
        var self = this;
        jsonrpc('/web/dataset/call_kw/crm.lead/crm_week', {
            model: 'crm.lead',
            method: 'crm_week',
            args: [{  by_all: true  }],
            kwargs: {},
        }).then(function(result) {
            $('#leads_this_year, #opp_this_year, #exp_rev_this_year, #rev_this_year, #ratio_this_year, #avg_time_this_year, #total_revenue_this_year').hide();
            $('#leads_this_quarter, #opp_this_quarter, #exp_rev_this_quarter, #rev_this_quarter, #ratio_this_quarter, #avg_time_this_quarter, #total_revenue_this_quarter').hide();
            $('#leads_this_month, #opp_this_month, #exp_rev_this_month, #rev_this_month, #ratio_this_month, #avg_time_this_month, #total_revenue_this_month').hide();

            $('#leads_this_week, #opp_this_week, #exp_rev_this_week, #rev_this_week, #ratio_this_week, #avg_time_this_week, #total_revenue_this_week').show().empty();

            $('#leads_this_week').append('<span>' + result.record + '</span>');
            $('#opp_this_week').append('<span>' + result.record_op + '</span>');
            $('#exp_rev_this_week').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev_exp + '</span>');
            $('#rev_this_week').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev + '</span>');
            $('#ratio_this_week').append('<span>' + parseFloat(result.lost_ratio).toFixed(2) + '%</span>');
            $('#avg_time_this_week').append('<span>' + result.avg_time + '&nbspsec</span>');
            $('#total_revenue_this_week').append('<span>' + result.opportunity_ratio_value + '%</span>');

            self.refreshActiveLeads("this_week");
        });
    }

    onclick_this_month(ev) {
        var self = this;
        jsonrpc('/web/dataset/call_kw/crm.lead/crm_month', {
            model: 'crm.lead',
            method: 'crm_month',
            args: [{  by_all: true  }],
            kwargs: {},
        }).then(function(result) {
            $('#leads_this_year, #opp_this_year, #exp_rev_this_year, #rev_this_year, #ratio_this_year, #avg_time_this_year, #total_revenue_this_year').hide();
            $('#leads_this_quarter, #opp_this_quarter, #exp_rev_this_quarter, #rev_this_quarter, #ratio_this_quarter, #avg_time_this_quarter, #total_revenue_this_quarter').hide();
            $('#leads_this_week, #opp_this_week, #exp_rev_this_week, #rev_this_week, #ratio_this_week, #avg_time_this_week, #total_revenue_this_week').hide();

            $('#leads_this_month, #opp_this_month, #exp_rev_this_month, #rev_this_month, #ratio_this_month, #avg_time_this_month, #total_revenue_this_month').show().empty();

            $('#leads_this_month').append('<span>' + result.record + '</span>');
            $('#opp_this_month').append('<span>' + result.record_op + '</span>');
            $('#exp_rev_this_month').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev_exp + '</span>');
            $('#rev_this_month').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev + '</span>');
            $('#ratio_this_month').append('<span>' + parseFloat(result.lost_ratio).toFixed(2) + '%</span>');
            $('#avg_time_this_month').append('<span>' + result.avg_time + '&nbspsec</span>');
            $('#total_revenue_this_month').append('<span>' + result.opportunity_ratio_value + '%</span>');

            self.refreshActiveLeads("this_month");
        });
    }

    onclick_this_quarter(ev) {
        var self = this;
        jsonrpc('/web/dataset/call_kw/crm.lead/crm_quarter', {
            model: 'crm.lead',
            method: 'crm_quarter',
            args: [{  by_all: true  }],
            kwargs: {},
        }).then(function(result) {
            $('#leads_this_year, #opp_this_year, #exp_rev_this_year, #rev_this_year, #ratio_this_year, #avg_time_this_year, #total_revenue_this_year').hide();
            $('#leads_this_month, #opp_this_month, #exp_rev_this_month, #rev_this_month, #ratio_this_month, #avg_time_this_month, #total_revenue_this_month').hide();
            $('#leads_this_week, #opp_this_week, #exp_rev_this_week, #rev_this_week, #ratio_this_week, #avg_time_this_week, #total_revenue_this_week').hide();

            $('#leads_this_quarter, #opp_this_quarter, #exp_rev_this_quarter, #rev_this_quarter, #ratio_this_quarter, #avg_time_this_quarter, #total_revenue_this_quarter').show().empty();

            $('#leads_this_quarter').append('<span>' + result.record + '</span>');
            $('#opp_this_quarter').append('<span>' + result.record_op + '</span>');
            $('#exp_rev_this_quarter').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev_exp + '</span>');
            $('#rev_this_quarter').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev + '</span>');
            $('#ratio_this_quarter').append('<span>' + parseFloat(result.lost_ratio).toFixed(2) + '%</span>');
            $('#avg_time_this_quarter').append('<span>' + result.avg_time + '&nbspsec</span>');
            $('#total_revenue_this_quarter').append('<span>' + result.opportunity_ratio_value + '%</span>');

            self.refreshActiveLeads("this_quarter");
        });
    }

    onclick_this_year(ev) {
        var self = this;
            jsonrpc('/web/dataset/call_kw/crm.lead/crm_year', {
                model: 'crm.lead',
                method: 'crm_year',
                args: [{  by_all: true  }],
                kwargs: {},
            }).then(function (result) {
            $('#leads_this_quarter, #opp_this_quarter, #exp_rev_this_quarter, #rev_this_quarter, #ratio_this_quarter, #avg_time_this_quarter, #total_revenue_this_quarter').hide();
            $('#leads_this_month, #opp_this_month, #exp_rev_this_month, #rev_this_month, #ratio_this_month, #avg_time_this_month, #total_revenue_this_month').hide();
            $('#leads_this_week, #opp_this_week, #exp_rev_this_week, #rev_this_week, #ratio_this_week, #avg_time_this_week, #total_revenue_this_week').hide();

            $('#leads_this_year, #opp_this_year, #exp_rev_this_year, #rev_this_year, #ratio_this_year, #avg_time_this_year, #total_revenue_this_year').show().empty();

            $('#leads_this_year').append('<span>' + result.record + '</span>');
            $('#opp_this_year').append('<span>' + result.record_op + '</span>');
            $('#exp_rev_this_year').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev_exp + '</span>');
            $('#rev_this_year').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev + '</span>');
            $('#ratio_this_year').append('<span>' + parseFloat(result.lost_ratio).toFixed(2) + '%</span>');
            $('#avg_time_this_year').append('<span>' + result.avg_time + '&nbspsec</span>');
            $('#total_revenue_this_year').append('<span>' + result.opportunity_ratio_value + '%</span>');

            self.refreshActiveLeads("this_year");
        });
    }

    onMounted() {
        const el = document.querySelector('#active_leads');
        if (el) el.innerHTML = (this.active_leads_count || 0).toString();
        const card = document.querySelector('.active_leads_card');
        if (card) {
            card.addEventListener('click', (ev) => {
                ev.preventDefault();
                this._openActiveLeadsList();
            });
        }
        
    }

    _openActiveLeadsList() {
        const action = {
            type: 'ir.actions.act_window',
            name: 'Active Leads',
            res_model: 'crm.lead',
            view_mode: 'tree,form',
            target: 'current',
            domain: [
                ['active', '=', true],
                ['stage_id.is_won', '=', false],
                ['stage_id.fold', '=', false],
            ],
        };
        this.action.doAction(action);
    }

    

    /**
     * Handles the revenue card action.
     * Initiates an action to display revenue-related data.
     * @param {Event} e - The event object.
     */
    revenue_card(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Revenue"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form,calendar',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [
                ['user_id', '=', session.uid],
                ['type', '=', 'opportunity'],
                ['stage_id', '=', 4]
            ],
            target: 'current',
        }, options)
    }
    /**
     * Initiates an action to display expected revenue data.
     * @param {Event} e - The event object.
     */
    exp_revenue(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Expected Revenue"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form,calendar',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [
                ['user_id', '=', session.uid],
                ['type', '=', 'opportunity'],
                ['active', '=', true]
            ],
            target: 'current',
        }, options)
    }
    /**
     * Initiates an action to display unassigned leads data.
     * @param {Event} e - The event object.
     */
    unassigned_leads(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Unassigned Leads"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form,calendar',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [
                ['user_id', '=', false],
                ['type', '=', 'lead']
            ],
            context: {
                'group_by': 'team_id'
            },
            target: 'current',
        }, options)
    }
    /**
     * Initiates an action to display opportunity data.
     * @param {Event} e - The event object.
     */
    opportunity(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Opportunity"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form,calendar',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [
                ['user_id', '=', session.uid],
                ['type', '=', 'opportunity']
            ],
            target: 'current',
        })
    }
    /**
     * Initiates an action to display leads assigned to the current user.
     * @param {Event} e - The event object.
     */
    my_lead(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("My Leads"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form,calendar',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [
                ['user_id', '=', session.uid]
            ],
            target: 'current',
        }, options)
    }
    /**
     * Handles the reverse breadcrumb action.
     * Updates the breadcrumb, fetches updated data, and reloads the dashboard.
     */
    on_reverse_breadcrumb() {
        var self = this;
        WebClient.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function() {
            self.$('.o_hr_dashboard').reload();
            self.render_dashboards();
        });
    }
    /**
     * Lifecycle hook triggered when the component is mounted.
     * Renders various charts and graphs upon mounting.
     */
    async onMounted() {
        this.renderElement();
        this.funnel_chart();
        this.render_annual_chart_graph();
        this.render_sales_activity_graph();
        this.render_leads_month_graph();
        this.render_revenue_count_pie();
        this.render_campaign_leads_graph();
        this.render_medium_leads_graph();
        this.render_source_leads_graph();
        this.onclick_lost_last_12months();
        this.render_lost_leads_by_stage_graph();
        this.render_priority_pie_chart();
    }
    /**
     * Render Priority Distribution Pie Chart
     */
    render_priority_pie_chart() {
        const ctx = document.getElementById("priority_pie");
        if (!ctx) {
            console.warn("Priority pie chart canvas not found");
            return;
        }

        jsonrpc('/web/dataset/call_kw/crm.lead/get_priority_distribution', {
            model: 'crm.lead',
            method: 'get_priority_distribution',
            args: [{}],
            kwargs: {},
        }).then(function(res) {
            console.log("Priority Data from Odoo:", res);

            // Handle jika response berupa list
            if (Array.isArray(res)) {
                res = res[0];
            }

            const counts = (res && res.counts) ? res.counts : {};
            const low = counts.low || 0;
            const middle = counts.middle || 0;
            const high = counts.high || 0;

            const data = [low, middle, high];
            const labels = ['Low', 'Middle', 'High'];

            // Kalau semua 0, tampilkan dummy
            const total = data.reduce((a, b) => a + b, 0);
            if (total === 0) {
                data[1] = 1; // tampilkan satu bagian middle biar chart tetap muncul
            }

            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: ['#28a745', '#ffc107', '#dc3545'], // green, yellow, red
                        borderColor: '#fff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = data.reduce((a, b) => a + b, 0);
                                    const percentage = total ? ((value / total) * 100).toFixed(2) : 0;
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }).catch(err => console.error("Error fetching priority data:", err));
    }


    /**
     * Renders a doughnut chart to display lost leads categorized by stage.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_lost_leads_by_stage_graph() {
        var self = this
        var ctx = $(".lost_leads_by_stage_graph");
        jsonrpc('/web/dataset/call_kw/crm.lead/get_lost_lead_by_stage_pie', {
            model: "crm.lead",
            method: "get_lost_lead_by_stage_pie",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "bottom",
                    labels: {
                        fontColor: "#333",
                        fontSize: 16
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
    /**
     * Handles the change event for the total lost CRM selection.
     * Determines the selected timeframe and triggers the respective method.
     * @param {Event} e - The event object.
     */
    change_total_loosed_crm(e) {
        e.stopPropagation();
        var $target = $(e.target);
        var value = $target.val();
        if (value == "lost_last_12months") {
            this.onclick_lost_last_12months($target.val());
        } else if (value == "lost_last_6months") {
            this.onclick_lost_last_6months($target.val());
        } else if (value == "lost_last_month") {
            this.onclick_lost_last_month($target.val());
        }
    }
    /**
     * Handles the click event for the 'lost_last_month' option.
     * Calls a JSON-RPC method to retrieve total lost CRM data for the last month.
     * Generates a bar chart to represent the lost CRM data.
     * @param {Event} ev - The event object.
     */
    onclick_lost_last_month(ev) {
        var self = this;
        self.initial_render = true;
        jsonrpc('/web/dataset/call_kw/crm.lead/get_total_lost_crm', {
            model: "crm.lead",
            method: "get_total_lost_crm",
            args: ['1'],
            kwargs: {},
        }).then(function(result) {
            var ctx = document.getElementById("canvas").getContext('2d');
            // Define the data
            var lost_reason = result.month // Add data values to array
            var count = result.count;
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: lost_reason, //x axis
                    datasets: [{
                        label: 'Count', // Name the series
                        data: count, // Specify the data values array
                        backgroundColor: '#66aecf',
                        borderColor: '#66aecf',
                        barPercentage: 0.5,
                        barThickness: 6,
                        maxBarThickness: 8,
                        minBarLength: 0,
                        borderWidth: 1, // Specify bar border width
                        type: 'bar', // Set this data to a line chart
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        });
    }
    /**
     * Handles the click event for displaying total lost CRM data for the last 6 months.
     * Retrieves and displays the data using Chart.js in a bar chart format.
     * @param {Event} ev - The event object.
     */
    onclick_lost_last_6months(ev) {
        var self = this;
        self.initial_render = true;
        jsonrpc('/web/dataset/call_kw/crm.lead/get_total_lost_crm', {
            model: "crm.lead",
            method: "get_total_lost_crm",
            args: ['6'],
            kwargs: {},
        }).then(function(result) {
            const canvas = document.getElementById("canvas");
            if (!canvas) {
                console.warn("Canvas element not found — Admin CRM section is hidden.");
                return;
            }
            const ctx = canvas.getContext('2d');

            const lost_reason = result.month;
            const count = result.count;

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: lost_reason,
                    datasets: [{
                        label: 'Count',
                        data: count,
                        backgroundColor: '#66aecf',
                        borderColor: '#66aecf',
                        barPercentage: 0.5,
                        barThickness: 6,
                        maxBarThickness: 8,
                        minBarLength: 0,
                        borderWidth: 1,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        });
    }

    onclick_lost_last_12months(ev) {
        var self = this;
        if (self.is_manager === true) {
            self.initial_render = true;
            jsonrpc('/web/dataset/call_kw/crm.lead/get_total_lost_crm', {
                model: "crm.lead",
                method: "get_total_lost_crm",
                args: ['12'],
                kwargs: {},
            }).then(function(result) {
                const canvas = document.getElementById("canvas");
                if (!canvas) {
                    console.warn("Canvas element not found — Admin CRM section is hidden.");
                    return;
                }
                const ctx = canvas.getContext('2d');

                const lost_reason = result.month;
                const count = result.count;

                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: lost_reason,
                        datasets: [{
                            label: 'Count',
                            data: count,
                            backgroundColor: '#66aecf',
                            borderColor: '#66aecf',
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1,
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: { beginAtZero: true },
                        },
                        responsive: true,
                        maintainAspectRatio: false,
                    }
                });
            });
        }
    }
    /**
     * Renders a doughnut chart to display lost leads categorized by reason.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_lost_leads_graph() {
        var self = this;
        var ctx = $(".lost_leads_graph");
        jsonrpc('/web/dataset/call_kw/crm.lead/get_lost_lead_by_reason_pie', {
            model: "crm.lead",
            method: "get_lost_lead_by_reason_pie",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "bottom",
                    labels: {
                        fontColor: "#333",
                        fontSize: 16
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
    /**
     * Renders a doughnut chart to display leads categorized by their source.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_source_leads_graph() {
        var self = this
        var ctx = $(".source_lead");
        jsonrpc('/web/dataset/call_kw/crm.lead/get_the_source_pie', {
            model: "crm.lead",
            method: "get_the_source_pie",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "right",
                    labels: {
                        fontColor: "#333",
                        fontSize: 14
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
    /**
     * Renders a doughnut chart to display leads categorized by their medium.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_medium_leads_graph() {
        var self = this
        var ctx = $(".medium_leads");
        jsonrpc('/web/dataset/call_kw/crm.lead/get_the_medium_pie', {
            model: "crm.lead",
            method: "get_the_medium_pie",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "right",
                    labels: {
                        fontColor: "#333",
                        fontSize: 14
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
    /**
     * Renders a doughnut chart to display leads categorized by their campaign source.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_campaign_leads_graph() {
        var self = this
        var ctx = $(".campaign_source");
        jsonrpc('/web/dataset/call_kw/crm.lead/get_the_campaign_pie', {
            model: "crm.lead",
            method: "get_the_campaign_pie",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "bottom",
                    labels: {
                        fontColor: "#333",
                        fontSize: 14
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
    /**
     * Renders a doughnut chart to display revenue count data.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_revenue_count_pie() {
        var self = this;
        var ctx = $(".revenue_count_pie_canvas");
        jsonrpc('/web/dataset/call_kw/crm.lead/revenue_count_pie', {
            model: "crm.lead",
            method: "revenue_count_pie",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#ff7c43",
                        "#f95d6a"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#ff7c43",
                        "#f95d6a"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "bottom",
                    labels: {
                        fontColor: "#333",
                        fontSize: 16
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
    /**
     * Renders a doughnut chart to display leads created each month.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_leads_month_graph() {
        var self = this
        var ctx = $(".lead_month");
        jsonrpc('/web/dataset/call_kw/crm.lead/get_lead_month_pie', {
            model: "crm.lead",
            method: "get_lead_month_pie",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "right",
                    labels: {
                        fontColor: "#333",
                        fontSize: 16
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
    /**
     * Renders a doughnut chart to display sales activity data.
     * Fetches data via JSON-RPC and generates a chart using Chart.js.
     */
    render_sales_activity_graph() {
        var self = this
        var ctx = $(".sales_activity");
        jsonrpc('/web/dataset/call_kw/crm.lead/get_the_sales_activity', {
            model: "crm.lead",
            method: "get_the_sales_activity",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderColor: [
                        "#003f5c",
                        "#2f4b7c",
                        "#f95d6a",
                        "#665191",
                        "#d45087",
                        "#ff7c43",
                        "#ffa600",
                        "#a05195",
                        "#6d5c16"
                    ],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "right",
                    labels: {
                        fontColor: "#333",
                        fontSize: 16
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                }
            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }
/**
 * Renders a bar chart to display annual target data.
 * Fetches data via JSON-RPC and generates a chart using Chart.js.
 */
render_annual_chart_graph() {
    const self = this;
    const ctx = $(".annual_target");

    jsonrpc('/web/dataset/call_kw/crm.lead/get_the_annual_target', {
        model: "crm.lead",
        method: "get_the_annual_target",
        args: [{}],
        kwargs: {},
    }).then(function (arrays) {
        // pastikan arrays berisi data valid
        if (!arrays || !Array.isArray(arrays[0]) || !Array.isArray(arrays[1])) {
            console.warn("⚠️ Data annual target tidak valid:", arrays);
            return;
        }

        const data = {
            labels: arrays[1],
            datasets: [{
                label: "",
                data: arrays[0],
                backgroundColor: ["#003f5c", "#f95d6a", "#ff7c43", "#6d5c16"],
                borderColor: ["#003f5c", "#f95d6a", "#ff7c43", "#6d5c16"],
                borderWidth: 1
            }]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            legend: { display: false },
            scales: {
                yAxes: [{
                    ticks: { beginAtZero: true, min: 0 }
                }]
            }
        };

        // buat chart hanya jika konteks ada
        if (ctx.length) {
            new Chart(ctx, {
                type: "bar",
                data: data,
                options: options
            });
        }
    }).catch(function (err) {
        console.error("❌ Gagal ambil data annual target:", err);
    });
}

/**
 * Renders a funnel (bar + pie) chart displaying lead stage data.
 * Fetches data via JSON-RPC and generates charts using Highcharts.
 */
funnel_chart() {
    const self = this;

    jsonrpc('/web/dataset/call_kw/crm.lead/get_lead_stage_data', {
        model: "crm.lead",
        method: "get_lead_stage_data",
        args: [{}],
        kwargs: {},
    }).then(function (callbacks) {
        // pastikan callbacks array of [label, value]
        if (!Array.isArray(callbacks)) {
            console.warn("⚠️ Data funnel chart kosong atau invalid:", callbacks);
            callbacks = [];
        }

        // ---- Bar Chart (Opportunity by Stage) ----
        const barContainer = document.getElementById("container");
        if (barContainer) {
            const barData = callbacks.map(item => [
                item && item[0] ? String(item[0]) : "",
                item && item[1] ? Number(item[1]) : 0
            ]);

            Highcharts.chart(barContainer, {
                chart: { type: "column" },
                title: { text: "Opportunity by Stage" },
                credits: { enabled: false },
                xAxis: {
                    type: "category",
                    title: { text: "Stages" }
                },
                yAxis: {
                    title: { text: "Number of Leads" }
                },
                legend: { enabled: false },
                series: [{
                    name: "Leads",
                    data: barData,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}'
                    }
                }],
            });
        }

        // ---- Pie Chart (Won vs Lost) ----
        let won_count = 0;
        let lost_count = 0;
        callbacks.forEach(function (item) {
            const name = item && item[0] ? item[0].toLowerCase() : "";
            const value = item && item[1] ? Number(item[1]) : 0;
            if (name === "won") won_count = value;
            if (name === "lost") lost_count = value;
        });

        const pieContainer = document.getElementById("won_lost_pie");
        if (pieContainer) {
            Highcharts.chart(pieContainer, {
                chart: { type: 'pie' },
                title: { text: null },
                credits: { enabled: false },
                plotOptions: {
                    pie: {
                        showInLegend: true,
                        dataLabels: { enabled: false },
                        size: '90%',
                        cursor: 'pointer',
                        point: {
                            events: {
                                click: function () {
                                    try {
                                        if (!self || !self.action) {
                                            console.warn("⚠️ Action Odoo tidak tersedia");
                                            return;
                                        }
                                        const context = {
                                            search_default_assigned_to_me: 1,
                                        };
                                        if (this.name === "Won") {
                                            context.search_default_won = 1;
                                        } else if (this.name === "Lost") {
                                            context.search_default_lost = 1;
                                        }
                                        self.action.doAction({
                                            type: 'ir.actions.act_window',
                                            res_model: 'crm.lead',
                                            view_mode: 'kanban',
                                            name: 'My Pipeline',
                                            views: [[false, 'kanban'], [false, 'form']],
                                            target: 'current',
                                            context: context,
                                        });
                                    } catch (err) {
                                        console.error("❌ Error buka pipeline:", err);
                                    }
                                }
                            }
                        }
                    }
                },
                legend: {
                    align: 'right',
                    verticalAlign: 'middle',
                    layout: 'vertical',
                    itemStyle: { fontSize: '14px', fontWeight: 'normal' }
                },
                series: [{
                    name: 'Leads',
                    colorByPoint: true,
                    data: [
                        { name: 'Won', y: Number(won_count) || 0, color: '#093FB4' },
                        { name: 'Lost', y: Number(lost_count) || 0, color: '#F5D2D2' }
                    ]
                }]
            });
        }
    }).catch(function (err) {
        console.error("❌ Gagal ambil data lead stage:", err);
    });
}

    /**
     * Fetches lead details via JSON-RPC and appends the data to specific HTML elements.
     */
    renderElement(ev) {
        var self = this;
        jsonrpc('/web/dataset/call_kw/crm.lead/lead_details_user', {
            model: "crm.lead",
            method: "lead_details_user",
            args: [{}],
            kwargs: {},
        }).then(function(result) {
            $('#leads_this_month').append('<span>' + result.record + '</span>');
            $('#opp_this_month').append('<span>' + result.record_op + '</span>');
            $('#exp_rev_this_month').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev_exp + '</span>');
            $('#rev_this_month').append('<span>' + self.monthly_goals[2] + '&nbsp' + result.record_rev + '</span>');
            $('#ratio_this_month').append('<span>' + parseFloat(result.record_ratio).toFixed(2) + '</span>');
            $('#avg_time_this_month').append('<span>' + result.avg_time + '&nbspsec' + '</span>');
            $('#total_revenue_this_month').append('<span>' + result.opportunity_ratio_value + '</span>');
            $('#target').append('<span>' + result.target + '</span>');
            $('#ytd_target').append('<span>' + result.ytd_target + '</span>');
            $('#difference').append('<span>' + result.difference + '</span>');
            $('#won').append('<span>' + result.won + '</span>');
        })
    }
}
CRMDashboard.template = "CRMdashboard"
registry.category("actions").add("crm_dashboard", CRMDashboard)

