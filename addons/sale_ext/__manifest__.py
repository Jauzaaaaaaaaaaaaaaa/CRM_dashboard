# -*- coding: utf-8 -*-
{
    'name': "Sale Extensions",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
1)Product show in Quotation Print
    """,

    'author': "Kaung Khant Zaw",
    'website': "https://www.idealab.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sale_pdf_quote_builder',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'report/ir_actions_report_templates.xml',
        'report/ir_actions_report.xml',        
        # 'views/purchase_order_views.xml'
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

