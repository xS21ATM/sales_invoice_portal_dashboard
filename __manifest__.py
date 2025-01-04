# -*- coding: utf-8 -*-
{
    'name': "Sales and Invoice Portal Dashboard",

    'summary': """
        Portal Features""",

    'description': """
        Portal Features
    """,

    'author': "A.T.M Shamiul Bashir",
    'website': "https://www.odoo.com/",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'hr', 'product', 'stock', 'contacts', 'portal', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/templates/portal/base.xml',
        'views/templates/portal/dashboard.xml',
        'views/templates/portal/sales.xml',
        'views/templates/portal/create_sale.xml',
        'views/templates/portal/create_sale_status.xml',
        'views/templates/portal/create_new_customer.xml',
        'views/templates/portal/create_new_customer_status.xml',
    ],
}
