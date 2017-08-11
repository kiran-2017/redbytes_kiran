# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ## Add HSN code field
    product_hsn_code = fields.Char(string="HSN Code")



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
