# -*- coding: utf-8 -*-
{
    'name': "CRM Extensions",

    'summary': "CRM Extension Master Data & CRM Dashboard",

    'description': """
        1) CRM Extension Master Data
        2) CRM Dashboard
    """,

    'author': "AMB05",
    'website': "https://github.com/AMB05",

    'category': 'CRM',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','crm',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/lead_master_data.xml',
        'data/timestep_data.xml',
        # 'views/crm_lead_view.xml',
        # 'views/crm_lead_category_views.xml'
        'views/lead_master_views.xml',
        'views/lead_master_menu.xml',
        'views/crm_lead_inherit_view.xml',
                
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

