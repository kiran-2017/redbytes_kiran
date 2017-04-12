# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    """ Inhertit for print customized reports for DC and Incoming Shipment for Sale and Purchase"""

    ## incoming shipment fields
    in_time = fields.Datetime(string="In Time")
    transporter_name = fields.Char(string="Transporter Name")
    vehical_no = fields.Char(string="Vehical No")
    received_by = fields.Char(string="Received By", default=lambda self: self.env.user.name)
    challan_date = fields.Date(string="Challan Date")
    challan_no = fields.Char(string="Challan No.")
    ics_lr_no = fields.Char(string="L.R. No.")
    picking_type_flag = fields.Boolean(string="Picking Type Flag", default=False)

    @api.multi
    def do_print_picking(self):
        """ Inherit for pass new customized report for Delivery Slip"""
        report_name = ""
        if self.picking_type_id.code == 'incoming':
            report_id = self.env["report"].get_action(self, 'technomark_reports.report_incoming_shipment')
            report_name = 'Incoming Shipment' + ' ' + self.name
            report_id.update({'print_report_name':report_name})
            report_id.update({'name':report_name})
            self.write({'printed': True})
            return report_id
        else:
            report_id = self.env["report"].get_action(self, 'technomark_reports.report_deliveryslip_inherited')
            report_name = 'Delivery Challan' + ' ' + self.name
            report_id.update({'print_report_name':report_name})
            self.write({'printed': True})
            return report_id

    @api.model
    def date_converted(self, date):
        """ This function convert date %Y-%m-%d %H:%M:%S to  %m/%d/%Y remove time from date"""
        if date:
            converted_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
            return converted_date

    @api.model
    def get_sale_order_line_data(self, origin, product_id):
        """ This function fetch data from SOL like bore, value operation, pn, case file no, etc on DC"""
        sale_order_obj = self.env['sale.order']
        if origin == 'incoming_shipment':
            return False
        res = []
        if origin:
            sale_order_line_id = sale_order_obj.search([('name', '=', origin)])
            for line in sale_order_line_id.order_line:
                if line.product_id.id == product_id.id:
                    return line ## return line to fetched data on qweb DC report

    @api.model
    def get_purchase_order_line_data(self, origin, product_id):
        """ This function fetch data from POL like approx weight etc on IS"""
        purchase_order_obj = self.env['purchase.order']
        res = []
        if origin:
            purchase_order_line_id = purchase_order_obj.search([('name', '=', origin)])
            for line in purchase_order_line_id.order_line:
                if line.product_id.id == product_id.id:
                    return line ## return line to fetched data on qweb IS report

    @api.model
    def get_cust_ref(self, origin):
        """ This function dsplay customer referance on qweb report for DC"""
        if origin == 'incoming_shipment':
            return False
        sale_order_obj = self.env['sale.order']
        if origin:
            sale_order_id = sale_order_obj.search([('name', '=', origin)])
            if sale_order_id:
                return sale_order_id.client_order_ref

            else:
                purchase_order_id = self.env['purchase.order'].search([('name', '=', origin)])
                if purchase_order_id:
                    return purchase_order_id.partner_ref
    @api.model
    def get_lot_serial_number(self, ids):
        """ This function return 1st and last lot_id from multiple lot_ids for a product"""
        pack_id_list = []
        pack_id_name_list = []
        serial_num = ""
        for pack_lot_id in ids:
            if pack_lot_id.lot_name:
                pack_id_name_list.append(pack_lot_id.lot_name)
            else:
                pack_id_list.append(pack_lot_id.lot_id.name)
        ## Logic for priting PO DC serial number as lot name
        if pack_id_name_list and len(pack_id_name_list):
            serial_num = pack_id_name_list[0] + '-' + pack_id_name_list[-1]
        elif pack_id_name_list and len(pack_id_name_list) == 1:
            serial_num = pack_id_name_list[0]

        ## Logic for priting SO DC serial number as lot id
        if pack_id_list and len(pack_id_list)>1:
            serial_num = pack_id_list[0] + '-' + pack_id_list[-1]
        elif pack_id_list and len(pack_id_list) == 1:
            serial_num = pack_id_list[0]
        return serial_num

class ProductTemplate(models.Model):
    _inherit = "product.template"
    """ Inherit class for add new fields to allow use of product weight
        at sale order line and calculate subtotal as weight * quantity * unit price
    """
    # This field allow to use product weight in Sale order Line
    is_weight_applicable = fields.Boolean(string="Allow To Use Weight")
