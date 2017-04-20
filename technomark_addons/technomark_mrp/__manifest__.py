# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Technomark MRP',
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
    'depends' : ['mrp', 'product', 'hr'],
    'data': [
            'views/product_views.xml',
            'views/mrp_bom_form_views.xml',
            'views/mrp_workorder_views.xml',
            'report/mrp_bom_structure_report_template.xml',
            'report/mrp_report_view_main.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
