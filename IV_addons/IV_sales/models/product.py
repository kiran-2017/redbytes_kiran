# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    pro_size = fields.Float(string="Size (mm)")
    pro_pn = fields.Char(string="PN")
    pro_material = fields.Char(string="Material")
    pro_operation = fields.Char(string="Operation")
    
