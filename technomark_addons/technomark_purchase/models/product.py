# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    """ Inherit class for add new fields to allow use of product weight
        at sale order line and calculate subtotal as weight * quantity * unit price
    """
    # This field allow to use product weight in Sale order Line
    is_weight_applicable = fields.Boolean(string="Allow To Use Weight")
