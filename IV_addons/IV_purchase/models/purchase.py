# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from num2words import num2words
import datetime

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    """
        Inherit class for priting new fields on PO
    """
    ## Add new fields to print on PO as taxes/duties
    taxes_duties = fields.Char(string="TAXES/DUTIES", default="As Applicable")



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    """ Inherit for Adding new fields and inherit functionality to calculate subtotal
        as per product weight
    """

    @api.model
    def create(self, vals):
        """ Inherit create method to validate POL qty field it should be > 0"""
        if vals and 'product_qty' in vals and vals['product_qty'] == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        res = super(PurchaseOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """ Logic for change approx_weight in PO line and apply new sub total"""
        """ Inherit write method to validate POL qty field it should be > 0"""
        if vals and 'product_qty' in vals and vals['product_qty'] == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        res = super(PurchaseOrderLine, self).write(vals)
        if res and self.product_qty == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Inherit function to pass approx weight to POL on change of product id"""
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        # pass material value on PO line if there
        if self.product_id and self.product_id.material:
            self.material = self.product_id.material
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()
        ## Logic to set weight to POL on chnage of product id and if weight set is true
        if self.product_id.is_weight_applicable:
            self.approx_weight = self.product_id.weight * self.product_qty or 0.0
        return result


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


    ## Add new fields on PO line
    serial_no = fields.Integer(compute='_get_po_line_seq', string="Sr.No", default=1)
    material = fields.Char(string="Material")
    approx_weight = fields.Float(string="Approx Weight(kg)")
