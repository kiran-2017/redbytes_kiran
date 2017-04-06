# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"
    """ Inherit class for adding new fields on sale order form to print on DC report"""

    ## Add new fields print on DC report
    delivery_date = fields.Date(string="Delivery Date")
    delivery_instructions = fields.Text(string="Delivery Instructions")
    insurance = fields.Text(string="Insurance")
    warranty = fields.Integer(string="Warranty(Months)")
    special_remarks = fields.Text(string="Special Remarks")



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    """ Inherit class for adding new fields on order line to print on DC report"""

    ## Add new fields
    bore = fields.Integer(string="Bore(mm)")
    valve = fields.Text(string="Valve")
    valve_operation = fields.Char(string="Valve Operation")
    pn = fields.Char(string="PN")
    case_file_number = fields.Char(string="Case File No")
    quantity = fields.Integer(string="Quantity")
    pro_delivery_date = fields.Date(string="Delivery Date")
