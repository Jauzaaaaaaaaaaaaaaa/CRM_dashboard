# -*- coding: utf-8 -*-
{
    'name': "CRM Extensions",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
1) Customer Category in Lead (Lead Category-master data)
2) Count state in Kanban View
    """,

    'author': "Kaung Khant Zaw",
    'website': "https://www.idealab.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'CRM',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','web','sales_team','sale_management',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        # 'report/ir_actions_report_templates.xml',
        # 'report/ir_actions_report.xml',        
        'views/crm_lead_category_views.xml',
        # 'views/assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',

    'assets': {
    'web.assets_backend': [
        # 'crm_ext/static/src/js/dashboard_view.js',
        # 'crm_ext/static/src/css/hide_graph.css',
    ],
},


}

