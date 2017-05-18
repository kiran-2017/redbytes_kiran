# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"
    # _order = "serial_no"

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
            self.od = self.product_id.od or False
            self.l = self.product_id.l or False
            self.b_id = self.product_id.b_id or False

    ## Using default sequnce field from BOM line keep for future
    # @api.multi
    # def _get_line_seq(self):
    #     """ This funcion generate PO line serial number sequence
    #         For each different PO sr. no. seq start from 1 for PO Line"""
    #     line_num = 1
    #     if self.ids:
    #         first_line_rec = self.browse(self.ids[0])
    #         for line_rec in first_line_rec.bom_id.bom_line_ids:
    #             line_rec.serial_no = line_num
    #             line_num += 1

    @api.model
    def create(self, vals):
        """ Inherit create function to pass sequnce value to serial number and relove issue for relocation of bom line"""
        if vals and 'sequence' in vals:
            vals['serial_no'] = vals['sequence']
        res = super(MrpBomLine, self).create(vals)
        return res


    ## Using default sequnce field to relove bom line relocation issue keep for future ref
    # serial_no = fields.Integer(compute="_get_line_seq", string="Sr No", default="1")
    serial_no = fields.Integer(string="Sr No", default="1")
    used_for = fields.Char(string="Used For")
    size = fields.Char(string="Size")
    material = fields.Char(string="Material")
    machine_drawing_no = fields.Char(string="Machine Drawing")
    casting_drawing_no = fields.Char(string="Casting Drawing")
    od = fields.Char(string="OD(mm)")
    l = fields.Char(string="L(mm)")
    b_id = fields.Char(string="ID(mm)")
