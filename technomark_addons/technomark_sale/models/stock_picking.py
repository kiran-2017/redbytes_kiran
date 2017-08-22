# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    """
        Inherit class for adding new fields and new funcionality
        and for adding other info tab fields on Stock picking form
    """

    @api.multi
    def do_new_transfer(self):
        """ Inherit this function to pass already existing lot id to DC"""
        op_vals = {}
        new_ids_write = {}
        stock_product_lot_obj = self.env['stock.production.lot']
        for pick in self:
            pack_operations_delete = self.env['stock.pack.operation']
            stock_pack_op_lot_obj = self.env['stock.pack.operation.lot']
            if not pick.move_lines and not pick.pack_operation_ids:
                raise UserError(_('Please create some Initial Demand or Mark as Todo and create some Operations. '))
            # In draft or with no pack operations edited yet, ask if we can just do everything
            if pick.state == 'draft' or all([x.qty_done == 0.0 for x in pick.pack_operation_ids]):
                # If no lots when needed, raise error
                picking_type = pick.picking_type_id
                if (picking_type.use_create_lots or picking_type.use_existing_lots):
                    for pack in pick.pack_operation_ids:
                        new_lot_ids = []
                        lot_id_list = []
                        ## Show warning for PO Delivery when lot id is not assign to product
                        if pack.product_id and pack.product_id.tracking != 'none' and pick.picking_type_id.code == 'incoming':
                            raise UserError(_('Some products require lots/serial numbers, so you need to specify those first!'))
                        if pack.product_id and pack.product_id.tracking != 'none' and pick.picking_type_id.code == 'outgoing':
                            # raise UserError(_('Some products require lots/serial numbers, so you need to specify those first!'))
                            ######## Write lot id assign logic here #####
                            ## To delete all existing lot ids
                            if pack.pack_lot_ids:
                                pack.pack_lot_ids.unlink()

                            ## Logic to search MO for So and assign lot id from tht MO
                            ## Convert origin to map with MO origin
                            new_origin = self.origin + ':WH: Stock -> CustomersMTO'
                            mo_id = self.env['mrp.production'].search([('origin', '=', new_origin),('state', '=', 'done'),('product_id', '=', pack.product_id.id)])
                            if mo_id:
                                stock_move_lot_ids = self.env['stock.move.lots'].search([('production_id', '=', mo_id.id), ('product_id', '=', pack.product_id.id)])
                                for stock_move_lot_id in stock_move_lot_ids:
                                    new_lot_ids.append(stock_move_lot_id.lot_id)
                            else:
                                ## Logic for creating new sequence number for lot assign product in SO DC
                                lot_ids = self.env['stock.production.lot'].search([('product_id', '=', pack.product_id.id)])
                                for lot_id in lot_ids:
                                    lot_id_list.append(lot_id)
                                for i in range(int(pack.product_qty)):
                                    if lot_id_list and i <= (len(lot_id_list)-1):
                                        new_lot_ids.append(lot_id_list[i])
                            ## Keep this for future referance
                            # if mo_ids:
                            #     for mo_id in mo_ids:
                            #         stock_move_lot_ids = self.env['stock.move.lots'].search([('production_id', '=', mo_id.id), ('product_id', '=', pack.product_id.id)])
                            #         for stock_move_lot_id in stock_move_lot_ids:
                            #             new_lot_ids.append(stock_move_lot_id.lot_id)
                            # else:
                            #     ## Logic for creating new sequence number for lot assign product in SO DC
                            #     lot_ids = self.env['stock.production.lot'].search([('product_id', '=', pack.product_id.id)])
                            #     for lot_id in lot_ids:
                            #         lot_id_list.append(lot_id)
                            #     for i in range(int(pack.product_qty)):
                            #         if lot_id_list and i <= (len(lot_id_list)-1):
                            #             new_lot_ids.append(lot_id_list[i])
                                    """
                                    # No need for now
                                    # serial no. fetching from MO orders
                                    # update logic
                                    # Keep it for future referance and use
                                    # next_sequence = self.env['ir.sequence'].get('stock.lot.serial')
                                    # seq_vals = {
                                    #         'name' : next_sequence,
                                    #         'product_id': pack.product_id.id,
                                    #         }
                                    # new_lot_id = stock_product_lot_obj.create(seq_vals)
                                    ## append all created new lot ids to this list
                                    # new_lot_ids.append(new_lot_id.id)
                                    """

                            ## If there is exact serial no. present then it will direct validate DO
                            ## If Serial no less than order qty user need to manually save allocation and then
                            ## Procced for backorder
                            for new_lot_id in new_lot_ids:
                                ## Logic to assign newly created lot id to related pack operation
                                op_vals = {'lot_id': new_lot_id.id, 'qty_todo': 1, 'qty': 1, 'operation_id': pack.id}
                                new_ids_write = {'lot_id': new_lot_id.id}
                                op_id = stock_pack_op_lot_obj.create(op_vals)
                                stock_pack_op_lot_obj.write({'lot_id': new_ids_write})
                view = self.env.ref('stock.view_immediate_transfer')
                wiz = self.env['stock.immediate.transfer'].create({'pick_id': pick.id})
                # TDE FIXME: a return in a loop, what a good idea. Really.
                return {
                    'name': _('Immediate Transfer?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.immediate.transfer',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }

            # Check backorder should check for other barcodes
            if pick.check_backorder():
                view = self.env.ref('stock.view_backorder_confirmation')
                wiz = self.env['stock.backorder.confirmation'].create({'pick_id': pick.id})
                # TDE FIXME: same reamrk as above actually
                return {
                    'name': _('Create Backorder?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.backorder.confirmation',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }
            for operation in pick.pack_operation_ids:
                if operation.qty_done < 0:
                    raise UserError(_('No negative quantities allowed'))
                if operation.qty_done > 0:
                    operation.write({'product_qty': operation.qty_done})
                else:
                    pack_operations_delete |= operation
            if pack_operations_delete:
                pack_operations_delete.unlink()
        self.do_transfer()
        return

    @api.model
    def create(self, vals):
        """ Inherit create method to pass default dc_mode as Non-Returnable when dc created from SO"""
        res = super(StockPicking, self).create(vals)
        if res and res.origin:
            sale_order_id = self.env['sale.order'].search([('name', '=', res.origin)])
            if sale_order_id and res.picking_type_id.code == 'outgoing':
                res.dc_mode = 'non_returnable'
        return res



    ## Add this fields on DC form to print on DC report
    transporter_name_id = fields.Many2one('transporter.name', string="Transporter Name")
    lr_no = fields.Char(string="L.R. No")
    lr_date = fields.Date(string="L.R. Date")
    vehical_registration_no = fields.Char(string="Vehicle Reg. No")
    basis_of_freight = fields.Selection([('To Pay', 'To Pay'), ('Paid', 'Paid')], 'Basis Of Freight', default='')
    road_permit_no = fields.Char(string="Road Permit No")
    delivery_type = fields.Selection([('door_delivery', 'DOOR DELIVERY'), ('godown_delivery', 'GODOWN DELIVERY')], 'Delivery Type', default='door_delivery')
    dc_mode = fields.Selection([('returnable', 'Returnable'), ('non_returnable', 'Non-Returnable')], 'Delivery Mode')


class TransporterName(models.Model):
    _name = "transporter.name"

    """ Newly added class to reate entries for transporter used on DC form"""

    name = fields.Char(string="Name")

class PackOperation(models.Model):
    """ Inherit this calss to add new field weight of product"""
    _inherit = "stock.pack.operation"

    weight = fields.Float(string='Weight')
    actual_weight = fields.Float(string="Actual Weight(kg)")

    @api.model
    def create(self, vals):
        """ Inherit create method to pass default unit weight of product on pack operation form in DC"""
        product_obj = self.env['product.product']
        order_obj = self.env['purchase.order']
        if vals and 'product_id' in vals:
            product_id = product_obj.search([('id', '=', vals['product_id'])])

        if vals and 'picking_id' in vals:
            picking_id = self.env['stock.picking'].search([('id', '=', vals['picking_id'])])
            if picking_id:
                order_id = order_obj.search([('name', '=', picking_id.origin)])
                for line in order_id.order_line:
                    if line.product_id.id == product_id.id and line.approx_weight:
                        vals['weight'] = line.approx_weight
        res = super(PackOperation, self).create(vals)
        return res
