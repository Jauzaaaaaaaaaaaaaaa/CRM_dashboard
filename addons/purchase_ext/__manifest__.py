# -*- coding: utf-8 -*-
{
    'name': "Purchase Extensions",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
1) Tag in Purchase Order 
2) Print preview in Purchase Order
3) UOM Col in Purchase Print 
4) UOM Col in Product List

    """,

    'author': "Kaung Khant Zaw",
    'website': "https://www.idealab.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','sales_team',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'report/ir_actions_report.xml',
        # 'report/ir_actions_purchase_report_template.xml',
        'views/purchase_order_views.xml'
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

