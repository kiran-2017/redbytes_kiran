# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    """
        Inherit class for adding new fields and new funcionality
        and for adding other info tab fields on Stock picking form
    """

    @api.model
    def create(self, vals):
        """ Inherit create method to pass default dc_mode as Non-Returnable when dc created from SO"""
        res = super(StockPicking, self).create(vals)
        if res and res.origin:
            sale_order_id = self.env['sale.order'].search([('name', '=', res.origin)])
            print sale_order_id,'--sale_order_id'
            if sale_order_id and res.picking_type_id.code == 'outgoing':
                res.dc_mode = 'non_returnable'
        return res



    ## Add this fields on DC form to print on DC report
    transporter_name_id = fields.Many2one('transporter.name', string="Transporter Name")
    lr_no = fields.Char(string="L.R. No")
    lr_date = fields.Date(string="L.R. Date")
    vehical_registration_no = fields.Char(string="Vehicka Reg. No")
    basic_of_freight = fields.Selection([('to_pay', 'To Pay'), ('paid', 'Paid')], 'Basic Of Freight', default='')
    road_permit_no = fields.Char(string="Road Permit No")
    delivery_type = fields.Selection([('door_delivery', 'DOOR DELIVERY'), ('godown_delivery', 'GODOWN DELIVERY')], 'Delivery Type', default='door_delivery')
    dc_mode = fields.Selection([('returnable', 'Returnable'), ('non_returnable', 'Non-Returnable')], 'Delivery Mode')


class TransporterName(models.Model):
    _name = "transporter.name"

    """ Newly added class to reate entries for transporter used on DC form"""

    name = fields.Char(string="Name")
