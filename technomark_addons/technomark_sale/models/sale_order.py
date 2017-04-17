# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"
    """ Inherit class for adding new fields on sale order form to print on DC report"""


    ## Add new fields print on DC report
    delivery_date = fields.Date(string="Delivery Date")
    delivery_instructions = fields.Text(string="Delivery Instructions")
    insurance = fields.Text(string="Insurance")
    warranty = fields.Integer(string="Warranty(Months)", default=12)
    special_remarks = fields.Text(string="Special Remarks")

    @api.multi
    def print_quotation(self):
        """ Inherit this function to change report name to add doc number to it"""
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        report = self.env['report'].get_action(self, 'sale.report_saleorder')
        report.update({'print_report_name':'Quotation_Order'+ ' ' + self.name})
        return report





class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    """ Inherit class for adding new fields on order line to print on DC report"""

    @api.model
    def create(self, vals):
        """ Inherit create method to validate SOL qty field it should be > 0"""
        if vals and 'product_uom_qty' in vals and vals['product_uom_qty'] == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        res = super(SaleOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """ Inherit write method to validate SOL qty field it should be > 0"""
        if vals and 'product_uom_qty' in vals and vals['product_uom_qty'] == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        res = super(SaleOrderLine, self).write(vals)
        if res and self.product_uom_qty == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        return res


    ## Add new fields
    bore = fields.Integer(string="Bore (mm)")
    valve = fields.Text(string="Valve")
    valve_operation = fields.Char(string="MO/EO")
    pn = fields.Char(string="PN")
    case_file_number = fields.Char(string="Case File No")
    quantity = fields.Integer(string="Quantity")
    pro_delivery_date = fields.Date(string="Delivery Date")
    ## Inherit this fields to remove decimal point from it
    # product_uom_qty = fields.Integer(string='Quantity', default=1)
