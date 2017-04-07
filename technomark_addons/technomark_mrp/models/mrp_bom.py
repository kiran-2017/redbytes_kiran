# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

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
