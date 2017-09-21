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

    ## Not required for now
    # @api.onchange('is_weight_applicable')
    # def _onchange_is_weight_applicable(self):
    #     """ This function assign UOM as Kg when is_weight_applicable is selected to True"""
    #     uom_obj = self.env['product.uom']
    #     uom_categ_obj = self.env['product.uom.categ']
    #     ## Get UOM id for No(s)
    #     product_uom_no_categ_ids = uom_categ_obj.search([('name','=','No')])
    #     print product_uom_no_categ_ids,'----------product_uom_no_categ_ids'
    #     product_uom_kg_categ_ids = uom_categ_obj.search([('name','=','Weight')])
    #     print product_uom_kg_categ_ids,'-------product_uom_kg_categ_ids'
    #     if product_uom_no_categ_ids or product_uom_kg_categ_ids:
    #         uom_no_ids = uom_obj.search([('name','=','No(s)'),('active','=',True),('category_id','in',[rec_id.id for rec_id in product_uom_no_categ_ids])])
    #         print uom_no_ids,'----------uom_no_ids'
    #
    #         uom_kg_ids = uom_obj.search([('name','=','kg'),('active','=',True),('category_id','in',[rec_id.id for rec_id in product_uom_kg_categ_ids])])
    #         print uom_kg_ids,'----------uom_kg_ids'
    #         if self.is_weight_applicable:
    #             print self.uom_id.name,'--------------UOM nameeeee'
    #             for uom_id in uom_kg_ids:
    #                 self.uom_id = uom_id.id
    #         else:
    #             for uom_id in uom_no_ids:
    #                 self.uom_id = uom_id.id

    @api.one
    @api.depends('property_cost_method', 'categ_id.property_cost_method')
    def _compute_cost_method(self):
        """ Inherit this Method to apply cost method from product category only"""
        #self.cost_method = self.property_cost_method or self.categ_id.property_cost_method
        self.cost_method = self.categ_id.property_cost_method
