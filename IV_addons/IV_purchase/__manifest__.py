# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'IV Purchase',
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
    'depends' : ['base','product', 'purchase', 'stock','IV_reports'],
    'data': [
        # 'views/product_view.xml',
        'views/purchase_view.xml',
        'report/purchase_report.xml',
        'report/purchase_order_template_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
