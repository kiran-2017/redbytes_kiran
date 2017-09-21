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
    _default_notes_val = """
    1. TAX INVOICE (Original for Recipient and Duplicate for Transporter alongwith Delivery challan ( Original and Duplicate)
    Applicable for Castings only
    2. Casting must be properly grinded and must be free from blow holes, mismatches with that of casting drawings.
    3. Thickness of casting must be homogeneous as per drawings and shall withstand hydrostatic pressure.
    4. Test valve of each heat shall be sent along with the castings bearing unique heat no.
    5. Heat no.,valve size, IVC Monogram and year of produce must be cast on all major castings.
    6. Patterns delivered to your foundry are absolute property of Indian Valve Pvt. Ltd., Nashik and the foundry has no right to take out any castings from the pattern, unless, a written order signed by the Director of the company is received by you.
    """
    ## Add new fields to print on PO as taxes/duties
    taxes_duties = fields.Char(string="TAXES/DUTIES", default="As Applicable")
    ## Inherit this field to pass default value as "DOOR DELIVERY" on PO
    incoterm_id = fields.Many2one('stock.incoterms', 'Incoterm', states={'done': [('readonly', True)]}, help="International Commercial Terms are a series of predefined commercial terms used in international transactions.", default=lambda self: self.env['stock.incoterms'].search([('name', '=', 'DOOR DELIVERY')]))
    insurance_term = fields.Many2one('po.insurance.term',string="Insurance Terms")
    freight_term = fields.Selection([('To Pay', 'To Pay'), ('Paid', 'Paid')], 'Freight Terms', default='')
    ## Inherit notes field to set default text on po
    notes = fields.Text('Terms and Conditions', default=_default_notes_val)

    @api.model
    def get_uom(self,line):
        """ This function assign UOM as Kg when is_weight_applicable is selected to True on PO report only"""
        uom_obj = self.env['product.uom']
        uom_categ_obj = self.env['product.uom.categ']
        ## Get UOM id for kg
        product_uom_kg_categ_ids = uom_categ_obj.search([('name','=','Weight')])
        if product_uom_kg_categ_ids:
            uom_kg_ids = uom_obj.search([('name','=','kg'),('active','=',True),('category_id','in',[rec_id.id for rec_id in product_uom_kg_categ_ids])])
            if line and line.product_id.is_weight_applicable:
                for uom_id in uom_kg_ids:
                    return uom_id.name

    @api.model
    def amount_in_words(self, total):
        """ This function convert amount in words format on PO qweb report"""
        if not total:
            return "Zero"
        if total:
            amount_in_words = num2words(total)
            return amount_in_words.title()


    @api.multi
    def print_quotation(self):
        self.write({'state': "sent"})
        report = self.env['report'].get_action(self, 'purchase.report_purchasequotation')
        report.update({'print_report_name':'Request For Quotation'+ ' ' + self.name})
        return report


    @api.model
    def amount_in_words(self, total):
        """ This function convert amount in words format on PO qweb report"""
        if total:
            amount_in_words = num2words(total)
            return amount_in_words.title()

    @api.model
    def date_converted(self, date):
        """ This function convert date %Y-%m-%d %H:%M:%S to  %m/%d/%Y remove time from date"""
        import datetime
        if date:
            converted_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            return converted_date


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
        ## Logic to change subtotal while creating PO
        if res and res.product_id.is_weight_applicable:
            res.approx_weight = res.product_id.weight * res.product_qty
            res.price_subtotal = res.approx_weight * res.price_unit
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
        # ## LOgic to set weight to POL on chnage of product id and if weight set is true
        ## rewrite bellow keep for reference only no use for now
        # if self.product_id.is_weight_applicable:
        #     self.approx_weight = self.product_id.weight * self.product_qty or 0.0
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
    def write(self, vals):
        """ Logic for change approx_weight in PO line and apply new sub total"""
        """ Inherit write method to validate POL qty field it should be > 0"""
        if vals and 'product_qty' in vals and self.product_id.is_weight_applicable:
            vals.update({'approx_weight': self.product_id.weight * vals['product_qty']})
            vals.update({'price_subtotal': self.approx_weight * self.price_unit})
        if vals and 'approx_weight' in vals and self.product_id.is_weight_applicable:
            # hide for now keep for future ref vals.update({'price_subtotal': vals['approx_weight'] * self.product_qty * self.price_unit})
            vals.update({'price_subtotal': vals['approx_weight'] * self.price_unit})
        if vals and 'product_qty' in vals and vals['product_qty'] == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        res = super(PurchaseOrderLine, self).write(vals)
        if res and self.product_qty == 0:
            raise UserError(_('You cannot enter product quantity as Zero'))
        return res


    @api.model
    def date_converted(self, date):
        """ This function convert date %Y-%m-%d %H:%M:%S to  %m/%d/%Y remove time from date"""
        if date:
            converted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
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

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        """ This function calculate total amount for PO after change of Quantity """
        if self.product_qty:
            self.approx_weight = self.product_id.weight * self.product_qty

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
                product_weight = line.product_id.weight * line.product_qty
                line.update({
                    ## Logic to calculate total tax on Approx Weight * rate * qty
                    'price_tax': (taxes['total_included'] * line.product_id.weight) - (taxes['total_excluded'] * line.product_id.weight),
                    'price_total': taxes['total_included'],
                    # 'price_subtotal': taxes['total_excluded'] * line.approx_weight, keep for future ref
                    'price_subtotal': line.price_unit * product_weight, ## subtotal is unit proce * total approx weight(unit weight * product qty)
                })
            else:
                ## Else default flow
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    ## Add new fields on PO line
    serial_no = fields.Integer(compute='_get_po_line_seq', string="Sr.No", default=1)
    material = fields.Char(string="Material")
    approx_weight = fields.Float(string="Approx Weight(kg)")
    ## Inherit product_qty to make it Integer to remove all deciaml points
    # product_qty = fields.Integer(string='Quantity', required=True)


class PoInsuranceTerm(models.Model):
    _name = 'po.insurance.term'
    ## Add new object for InsuranceTerm data entry
    name = fields.Char(string="Name")
