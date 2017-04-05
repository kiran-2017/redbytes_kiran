# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    bore = fields.Integer(string="Bore(mm)")
    valve = fields.Text(string="Valve")
    valve_operation = fields.Char(string="Valve Operation")
    pn = fields.Char(string="PN")
    case_file_number = fields.Char(string="Case File No")
    quantity = fields.Integer(string="Quantity")
    pro_delivery_date = fields.Date(string="Delivery Date")
