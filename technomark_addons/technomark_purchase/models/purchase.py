# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from num2words import num2words
import datetime

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    """
        Inherit class for priting new fields on PO
    """


    @api.model
    def amount_in_words(self, total):
        """ This function convert amount in words format on PO qweb report"""
        if total:
            amount_in_words = num2words(total)
            return amount_in_words

    @api.model
    def date_converted(self, date):
        """ This function convert date %Y-%m-%d %H:%M:%S to  %m/%d/%Y remove time from date"""
        if date:
            converted_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
            return converted_date


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    """ Inherit for Adding new fields and inherit functionality to calculate subtotal
        as per product weight
    """

    @api.multi
    def write(self, vals):
        """ Logic for change approx_weight in PO line and apply new sub total"""
        if vals and 'approx_weight' in vals and self.product_id.is_weight_applicable:
            vals.update({'price_subtotal': vals['approx_weight'] * self.product_qty * self.price_unit})
        res = super(PurchaseOrderLine, self).write(vals)
        return res

    @api.model
    def date_converted(self, date):
        """ This function convert date %Y-%m-%d %H:%M:%S to  %m/%d/%Y remove time from date"""
        if date:
            converted_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
            return converted_date


    @api.multi
    def _get_po_line_seq(self):
        """ This funcion generate PO line serial number sequence
            For each different PO sr. no. seq start from 1 for PO Line"""
        line_num = 1
        if self.ids:
        	first_line_rec = self.browse(self.ids[0])
        	for line_rec in first_line_rec.order_id.order_line:
        		line_rec.serial_no = line_num
        		line_num += 1

    @api.onchange('approx_weight')
    def _onchange_approx_weight(self):
        """ This function calculate total amount for PO after change of appprox weight"""
        if self.product_id.is_weight_applicable:
            self._compute_amount()


    # @api.multi
    # def _calculate_approx_weight(self):
    ## No use for now keep it for future referance
    #     for po_line_id in self:
    #         if po_line_id.product_id.is_weight_applicable:
    #             po_line_id.approx_weight = po_line_id.product_id.weight * po_line_id.product_qty

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        """" Inherit function to callculate sub total on aprrox weight is applicable"""
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            if line.product_id.is_weight_applicable:
                # product_weight = line.product_id.weight
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'] * line.approx_weight,
                })
            else:
                ## Else default flow
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    ## Add new fields on PO line
    serial_no = fields.Integer(compute='_get_po_line_seq', string="Sr.No")
    material = fields.Char(string="Material")
    approx_weight = fields.Float(related="product_id.weight", string="Approx Weight(kg)")
