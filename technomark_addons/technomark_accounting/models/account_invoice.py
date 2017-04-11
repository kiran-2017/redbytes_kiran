# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from num2words import num2words

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    """ Inherit this call for adding new fields on TAX INVOICE"""

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow Inherited to pass Tax Invoice ID
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'technomark_accounting.report_tax_invoice')

    ## Add new fields to print on TAX Invoice On Invoice object
    buyer_order_no = fields.Char(string="Buyer Order No")
    despateched_doc_no = fields.Char(string="Dispatched Document Number")
    despatched_through = fields.Char(string="Despatched Through")
    destination = fields.Char(string="Destination")
    other_ref = fields.Char(string="Other Ref")

    @api.model
    def get_product_line_info(self, origin, product_id):
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
    def amount_in_words(self, total):
        """ This function convert amount in words format on PO qweb report"""
        if not total:
            return "Zero"
        if total:
            amount_in_words = num2words(total)
            return amount_in_words

    @api.model
    def get_bank_details(self, company_id, partner_id):
        """ This function return bank id for company on qweb to feth bank details"""
        bank_obj = self.env['res.partner.bank']
        if company_id:
            bank_id = bank_obj.search([('company_id', '=', company_id.id), ('partner_id', '=', partner_id.id)])
            return bank_id

    @api.model
    def get_delcaration(self, origin):
        """ This function return declaration defined on SO or PO form on qweb report of Tax invoice"""
        so_obj = self.env['sale.order']
        po_obj = self.env['purchase.order']
        if origin:
            so_id = so_obj.search([('name', '=', origin)])
            if so_id:
                return so_id.note
            else:
                po_id = po_obj.search([('name', '=', origin)])
                if po_id:
                    return po_id.notes

    @api.model
    def get_order_data(self, origin):
        """ This function return data for SO or PO form on qweb report of Tax invoice"""
        so_obj = self.env['sale.order']
        po_obj = self.env['purchase.order']
        if origin:
            so_id = so_obj.search([('name', '=', origin)])
            if so_id:
                return so_id.incoterm.name
            else:
                po_id = po_obj.search([('name', '=', origin)])
                if po_id:
                    return po_id.incoterm_id.name

    @api.model
    def get_delivery_date(self, origin):
        """ This function return data for SO or PO form on qweb report of Tax invoice"""
        so_obj = self.env['sale.order']
        po_obj = self.env['purchase.order']
        if origin:
            so_id = so_obj.search([('name', '=', origin)])
            if so_id:
                return so_id.delivery_date
            else:
                po_id = po_obj.search([('name', '=', origin)])
                if po_id:
                    return po_id.date_planned

    @api.model
    def get_delivery_note(self, origin):
        """ This function return data for SO or PO form on qweb report of Tax invoice"""
        so_obj = self.env['sale.order']
        if origin:
            so_id = so_obj.search([('name', '=', origin)])
            if so_id:
                return so_id.special_remarks

    @api.model
    def get_lot_serial_number(self, origin, product_id):
        """ This function return lot_id from multiple lot_ids for a product"""
        pack_id_list = []
        if origin:
            order_id = self.env['sale.order'].search([('name', '=', origin)])
            if not order_id:
                order_id = self.env['purchase.order'].search([('name', '=', origin)])
        if order_id:
            for picking_id in order_id.picking_ids:
                if picking_id.state == 'done':
                    pack_operation_ids = [pack_id for pack_id in picking_id.pack_operation_product_ids]
                    for pack_operation_id in pack_operation_ids:
                        if pack_operation_id.product_id.id == product_id.id:
                            for lot_id in pack_operation_id.pack_lot_ids:
                                pack_id_list.append(lot_id.lot_id.name)
        return pack_id_list
