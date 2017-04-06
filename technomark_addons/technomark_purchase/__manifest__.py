# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Technomark Purchase',
    'version' : '1.1',
    'summary': 'Purchase',
    'sequence': 30,
    'description': """
Purchase
========
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Sale',
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['base','product', 'purchase', 'stock', 'technomark_reports'],
    'data': [
            'views/purchase_views.xml',
            'views/product_views.xml',
            'views/res_partner_views.xml',
            'views/stock_picking_views.xml',
            'report/purchase_order_templates.xml',
            'report/purchase_report.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
