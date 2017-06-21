# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from num2words import num2words
import datetime
from odoo.exceptions import UserError, ValidationError

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
            return amount_in_words.title()

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
    def date_converted(self, date):
        """ This function convert date %Y-%m-%d %H:%M:%S to  %m/%d/%Y remove time from date"""
        if date:
            converted_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            return converted_date

    @api.model
    def get_delivery_date(self, origin):
        """ This function return data for SO or PO form on qweb report of Tax invoice"""
        so_obj = self.env['sale.order']
        po_obj = self.env['purchase.order']
        if origin:
            so_id = so_obj.search([('name', '=', origin)])
            for pick in so_id.picking_ids:
                return pick
            # if so_id: Hide for now keep for future
            #     return so_id.delivery_date
            else:
                po_id = po_obj.search([('name', '=', origin)])
                # if po_id: Hide for now keep for future
                #     return po_id.date_planned
                for pick in po_id.picking_ids:
                    return pick

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



class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    """ Inherit this class to add new fields in invoice lines"""

    inv_actual_weight = fields.Float(string="Actual Weight(kg)")

    @api.model
    def create(self, vals):
        """ Inherit this function to calculate invoice  amount
            on basic of picking weight and received qty
        """

        inv_line = []
        if vals and 'purchase_line_id' in vals:
            ## Fetched all moves related to PO
            stock_move_ids = self.env['stock.move'].search([('purchase_line_id', '=', vals.get('purchase_line_id')),('state', '=', 'done')])
            ## Get picking ids from stock_moves
            picking_ids = [rec.picking_id for rec in stock_move_ids]
            ## Get operation ids from picking
            stock_pack_operation_ids = self.env['stock.pack.operation'].search([('picking_id', 'in', [picking_id.id for picking_id in picking_ids])])
        ## Create Invoice
        res = super(AccountInvoiceLine, self).create(vals)
        if res:
            inv_line.append(res)

        ## Logic to apply new actual weight and chnage invoice total
        if vals and 'purchase_line_id' in vals:
            for operation_id in stock_pack_operation_ids:
                for line in inv_line:
                    if line.product_id.is_weight_applicable and line.product_id.id == operation_id.product_id.id:
                        line.inv_actual_weight = operation_id.actual_weight
                        line.price_subtotal = line.price_unit * line.quantity * operation_id.actual_weight
                        self._compute_price()
        return res

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'inv_actual_weight')
    def _compute_price(self):
        """ Inherit this function to add actual weight calculation for invoice """

        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        ## Add actual_weight here in this field
        if self.invoice_id.type == 'in_invoice' or self.invoice_id.type == 'in_refund':
            if self.product_id.is_weight_applicable:
                self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] * self.inv_actual_weight if taxes else self.quantity * price
            else:
                self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        elif self.invoice_id.type == 'out_invoice' or self.invoice_id.type == 'out_refund':
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price

        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    def _set_additional_fields(self, invoice):
        """ Some modules, such as Purchase, provide a feature to add automatically pre-filled
            invoice lines. However, these modules might not be aware of extra fields which are
            added by extensions of the accounting module.
            This method is intended to be overridden by these extensions, so that any new field can
            easily be auto-filled as well.
            :param invoice : account.invoice corresponding record
            :rtype line : account.invoice.line record
        """
        ## Add logic to assign Actual Weight from Incoming Shipment
        ## Fetched all moves related to PO
        if self.purchase_line_id:
            stock_move_ids = self.env['stock.move'].search([('purchase_line_id', '=', self.purchase_line_id.id),('state', '=', 'done')])
            ## Get picking ids from stock_moves
            picking_ids = [rec.picking_id for rec in stock_move_ids]
            ## Get operation ids from picking
            stock_pack_operation_ids = self.env['stock.pack.operation'].search([('picking_id', 'in', [picking_id.id for picking_id in picking_ids])])
            for operation_id in stock_pack_operation_ids:
                for line in self:
                    if line.product_id.is_weight_applicable and line.product_id.id == operation_id.product_id.id:
                        ## Assign Actual Weight to each line of Invoice id weight is allow to product
                        line.inv_actual_weight = operation_id.actual_weight
        pass
