# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Technomark Accounting',
    'version' : '1.1',
    'summary': 'Accounting',
    'sequence': 30,
    'description': """
Accounting
==========
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Accounting',
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['account', 'account_accountant', 'base_vat'],
    'data': [
            'views/account_invoice_view.xml',
            'views/res_company_views.xml',
            'views/res_partner_views.xml',
            'report/account_report_views.xml',
            'report/report_tax_invoice.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
