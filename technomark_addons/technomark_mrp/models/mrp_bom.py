# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Inherit onchange function to pass material, size , etc values
        from product form while selecting product on BOM line"""
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            ## Pass all values from prodcut form onchange of product id
            self.material = self.product_id.material
            self.machine_drawing_no = self.product_id.machine_drawing_no
            self.casting_drawing_no = self.product_id.casting_drawing_no
            self.size = self.product_id.size

    @api.multi
    def _get_line_seq(self):
        """ This funcion generate PO line serial number sequence
            For each different PO sr. no. seq start from 1 for PO Line"""
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.bom_id.bom_line_ids:
                line_rec.serial_no = line_num
                line_num += 1

    serial_no = fields.Integer(compute="_get_line_seq", string="Sr No", default="1")
    used_for = fields.Char(string="Used For")
    size = fields.Char(string="Size")
    material = fields.Char(string="Material")
    machine_drawing_no = fields.Char(string="Machine Drawing")
    casting_drawing_no = fields.Char(string="Casting Drawing")
