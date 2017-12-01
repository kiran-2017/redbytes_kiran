# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    """
        Inherit class for adding new fields and new funcionality
        and for hiding Incoming Shipment menu on Stock picking form
    """


    # @api.multi
    # def do_print_picking(self):
    #     """ Inherit for pass new customized report for Delivery Slip"""
    #     self.write({'printed': True})
    #     return self.env["report"].get_action(self, 'technomark_reports.report_deliveryslip_inherited')

    @api.model
    def create(self, vals):
        """ Logic for passing picking_type_flag value on stock picking form"""
        stock_pick_obj = self.env['stock.picking.type']
        if vals and 'picking_type_id' in vals:
            stock_picking_type_id = stock_pick_obj.search([('id', '=', vals['picking_type_id'])])
            if stock_picking_type_id and stock_picking_type_id.code == 'incoming':
                vals.update({'picking_type_flag':True})
            else:
                vals.update({'picking_type_flag':False})
        res = super(StockPicking, self).create(vals)
        if res:
            res.in_time = False
            res.transporter_name = ""
            res.vehical_no = ""
            res.challan_date = False
            res.challan_no = ""
            res.ics_lr_no = ""
        return res

    # Flag for vsible/hide Incoming Shipment View on StockPicking
    picking_type_flag = fields.Boolean(string="Picking Type Flag", default=False)
