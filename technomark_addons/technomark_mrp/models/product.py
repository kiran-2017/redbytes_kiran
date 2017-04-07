# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    size = fields.Char(string="Size")
    material = fields.Char(string="Material")
    machine_drawing_no = fields.Char(string="Machine Drawing No")
    casting_drawing_no = fields.Char(string="Casting Drawing No")
