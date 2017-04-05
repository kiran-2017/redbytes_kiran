# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Technomark Reports',
    'version' : '1.1',
    'summary': 'Reports',
    'sequence': 30,
    'description': """
Sale
====
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Report',
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['product', 'sale', 'stock', 'purchase'],
    'data': [
            'views/stock_report_views.xml',
            'report/incoming_shipment.xml',
            'report/report_deliveryslip.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
