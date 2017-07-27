# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit = "mrp.bom"
    """
        Inherit class for add bom cost calculation logic
    """

    @api.multi
    def _compute_total_cost_of_raw_material(self):
        """ Function calculate total cost for bom cost lines """
        for rec in self.bom_cost_lines_ids:
            self.total_cost_of_raw_material += rec.total_cost


    ## Add bom cost lines field here
    bom_cost_lines_ids = fields.One2many("bom.cost.lines", "mrp_bom_id", string="Bom Cost")
    total_cost_of_raw_material = fields.Float(compute="_compute_total_cost_of_raw_material", string="Total Cost of Raw Materials")
    ## this fields check is bom lines get load or not
    is_load_bom_cost_lines = fields.Boolean(string="Load Bom Cost Lines", default=False)

    @api.multi
    def load_bom_cost_lines(self):
        """
            Function which create bom cost lines on BOM form
            logic is -
            if product weight applicable, total_cost = quantity * weight * unit_cost
            else, total_cost = quantity * unit_cost
        """
        ## Define object here
        bom_cost_obj = self.env['bom.cost.lines']

        for line in self.bom_line_ids:
            bom_cost_line_vals = {
                'product_id': line.product_id.id,
                'quantity': line.product_qty,
                'unit_cost': line.product_id.standard_price,
                'weight': line.product_id.weight if line.product_id.is_weight_applicable else 0.00,
                'mrp_bom_id': self.id
            }
            ## Create new records for bom cost lines
            bom_cost_obj.create(bom_cost_line_vals)
        ## set bom cost line loaded flag true
        self.is_load_bom_cost_lines = True

    @api.multi
    def update_bom_cost_lines(self):
        """
            This function update BOM COST lines
            as any field like price or quantity get changed
        """
        bom_cost_obj = self.env['bom.cost.lines']
        for line in self.bom_line_ids:
            bom_cost_line_vals = {
                'product_id': line.product_id.id,
                'quantity': line.product_qty,
                'unit_cost': line.product_id.standard_price,
                'weight': line.product_id.weight if line.product_id.is_weight_applicable else 0.00,
                'mrp_bom_id': self.id
            }
            bom_cost_line_ids = bom_cost_obj.search([('product_id','=',line.product_id.id),('mrp_bom_id','=',line.bom_id.id),('quantity','=',line.product_qty)])
            if not bom_cost_line_ids:
            #     ## if in bom new line added then while updating add line to bom cost line
                bom_cost_line_ids = bom_cost_obj.search([('product_id','=',line.product_id.id),('mrp_bom_id','=',line.bom_id.id)])
                if not bom_cost_line_ids:
                    bom_cost_obj.create(bom_cost_line_vals)
            for cost_line in bom_cost_line_ids:
                cost_line.write(bom_cost_line_vals)


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
