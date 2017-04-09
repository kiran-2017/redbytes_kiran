# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockMove(models.Model):
    """ Inherit this calss to remove all decimal points from quantity fields"""
    _inherit = 'stock.move'

    product_uom_qty = fields.Integer(
        'Quantity',
        default=1, required=True, states={'done': [('readonly', True)]},
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")

class PackOperation(models.Model):
    """ Inherit this calss to remove all decimal points from quantity fields"""
    _inherit = "stock.pack.operation"

    product_qty = fields.Integer('To Do', default=1, required=True)
    ordered_qty = fields.Integer('Ordered Quantity')
    qty_done = fields.Integer('Done')

class AccountInvoiceLine(models.Model):
    """ Inherit this calss to remove all decimal points from quantity fields"""
    _inherit = "account.invoice.line"

    quantity = fields.Integer(string='Quantity', required=True, default=1)
