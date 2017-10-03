# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'IV Sale',
    'version' : '1.1',
    'summary': 'Sale',
    'sequence': 30,
    'description': """
Sale
====
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Sale',
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['product', 'sale', 'stock', 'project', 'sale_stock','document','IV_reports','mail','mrp','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/product_view.xml',
        'views/account_invoice_view.xml',
        'views/stock_picking_view.xml',
        'data/mail_template_data.xml',
        'views/sent_docs_by_mail_menu.xml',
        'data/sent_gad_mail_template.xml',
        'data/sent_qap_mail_template.xml',
        'data/sent_tpi_mail_template.xml',
        'views/ir_attachment_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
