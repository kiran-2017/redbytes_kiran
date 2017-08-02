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

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Inherit onchange function to pass material, size , etc values
        from product form while selecting product on BOM line"""
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id or False
            ## Pass all values from prodcut form onchange of product id
            self.material = self.product_id.material or False
            self.machine_filename = self.product_id.machine_filename or False
            self.machine_drawing_no = self.product_id.machine_drawing_no or False
            self.machine_drawing_file = self.product_id.machine_drawing_no_file or False

            self.casting_filename = self.product_id.casting_filename or False
            self.casting_drawing_no = self.product_id.casting_drawing_no or False
            self.casting_drawing_file = self.product_id.casting_drawing_no_file or False

            self.raw_size = self.product_id.raw_size or False
            self.finished_size = self.product_id.finished_size or False

    @api.model
    def create(self, vals):
        """ Inherit create function to pass sequnce value to serial number and relove issue for relocation of bom line"""
        if vals and 'sequence' in vals:
            vals['serial_no'] = vals['sequence']
        res = super(MrpBomLine, self).create(vals)
        return res


    serial_no = fields.Integer(string="Sr No", default="1")
    used_for = fields.Char(string="Used For")
    raw_size = fields.Char(string="Size(Raw)")
    finished_size = fields.Char(string="Size(Finished)")
    material = fields.Char(string="Material")
    machine_drawing_no = fields.Char(string="Machine Drawing")
    machine_drawing_file = fields.Binary(string="Machine Drawing File")
    machine_filename = fields.Char('Machine File name', store=True)
    casting_drawing_no = fields.Char(string="Casting Drawing")
    casting_drawing_file = fields.Binary(string="Casting Drawing")
    casting_filename = fields.Char('Casting File name', store=True)
