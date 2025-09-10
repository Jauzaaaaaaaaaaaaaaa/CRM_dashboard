# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Extensions",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
1) Choose Pic (Employee) for each line of workorder
2) Add serial Number in Manufacturing Order(Not automatically)
3) Delay State and Delay Reason in Manufacturing Order

    """,

    'author': "Kaung Khant Zaw",
    'website': "https://www.idealab.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'widzards/wizard_delay_reason_views.xml',
        'views/mrp_workorder_views.xml',
        'views/mrp_production_views.xml',
        
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

