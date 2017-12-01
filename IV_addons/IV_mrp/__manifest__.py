# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'IV MRP',
    'version' : '1.1',
    'summary': 'MRP',
    'sequence': 30,
    'description': """
Accounting
==========
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'mrp',
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['mrp', 'product','document'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/mrp_bom_form_views.xml',
        'report/mrp_report_menu_view.xml',
        'report/mrp_bom_structure_template.xml',
        'report/mrp_bom_cost_report_template.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
