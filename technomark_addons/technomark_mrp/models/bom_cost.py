# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class BomCostLines(models.Model):
    _name = "bom.cost.lines"
    """ Add new class for bom cost calculation sho on BOM"""


    @api.multi
    @api.depends('quantity', 'unit_cost', 'weight')
    def _compute_bom_total_cost(self):
        """
            Funcion to calculate total_cost of each bom line
            logic is,
            if product weight is applicable, total_cost = quantity * weight * unit_cost
            else, total_cost = quantity * unit_cost
        """
        for rec in self:
            if rec.product_id.is_weight_applicable:
                rec.total_cost = rec.quantity * rec.weight * rec.unit_cost
            else:
                rec.total_cost = rec.quantity * rec.unit_cost


    ## Add fields here
    product_id = fields.Many2one('product.product', string="Raw Materials")
    quantity = fields.Float(string="Quantity")
    unit_cost = fields.Float(string="Unit Cost")
    weight = fields.Float(string="Weight(Kg)")
    total_cost = fields.Float(compute="_compute_bom_total_cost", string="Total Cost")
    mrp_bom_id = fields.Many2one("mrp.bom", string="Bom Id")
