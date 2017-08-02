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

    # @api.one
    # @api.depends('property_cost_method', 'categ_id.property_cost_method')
    # def _compute_cost_method(self):
    #     """ Inherit this Method to apply cost method from product category only"""
    #     #self.cost_method = self.property_cost_method or self.categ_id.property_cost_method
    #     self.cost_method = self.categ_id.property_cost_method
