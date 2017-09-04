# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"


    # @api.one
    # @api.constrains('product_hsn_code')
    # def _check_product_hsn_code(self):
    #     """
    #         Apply constrains for HSN code to accept only
    #         unique values
    #     """
    #     hsn_code_list = []
    #     product_template_ids = self.search([('id','!=', self.id)])
    #     for product_template_id in product_template_ids:
    #         if product_template_id.product_hsn_code:
    #             hsn_code_list.append(product_template_id.product_hsn_code)
    #     if self.product_hsn_code in hsn_code_list:
    #         raise ValidationError(_('A HSN Code can\'t have duplicate values.'))


    ## Add HSN code field on product template form
    product_hsn_code = fields.Char(string="HSN Code")


class Product(models.Model):
    _inherit = "product.product"

    ## Add HSN CODE field on product form
    product_hsn_code = fields.Char(related="product_tmpl_id.product_hsn_code", string="HSN Code")


## Not required keep for future referance
# class Product(models.Model):
#     _inherit = "product.product"
#     """ Inherit this class to change default display name for product in sale order line"""
#
#     @api.multi
#     def name_get(self):
#         """ Inherit this function to change display name for product on SOL
#             add product decription in product name itself
#         """
#         result = []
#         names = []
#         for rec in self:
#             if rec.default_code:
#                 names = ['['+rec.default_code+']']
#             if rec.name:
#                 names.append(rec.name)
#             if rec.description_sale:
#                 names.append(rec.description_sale)
#             result.append((rec.id, ' - '.join(names)))
#         return result
