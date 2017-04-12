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

    @api.multi
    def do_new_transfer(self):
        """ Inherit this function to pass already existing lot id to DC"""
        op_vals = {}
        new_ids_write = {}
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
                        if pack.product_id and pack.product_id.tracking != 'none':
                            # raise UserError(_('Some products require lots/serial numbers, so you need to specify those first!'))
                            ######## Write lot id assign logic here #####
                            product_lot_ids = self.env['stock.production.lot'].search([('product_id', '=', pack.product_id.id)])
                            if pack.pack_lot_ids:
                                pack.pack_lot_ids.unlink()
                            if not pack.pack_lot_ids:
                                product_lot_id_list = [product_lot_id.id for product_lot_id in product_lot_ids]
                                product_lot_id_list.reverse()
                                for i in range(int(pack.product_qty)):
                                    if i < len(product_lot_id_list):
                                        new_lot_ids.append(product_lot_id_list[i])
                            for new_lot_id in new_lot_ids:
                                op_vals = {'lot_id': new_lot_id, 'qty_todo': 1, 'qty': 1, 'operation_id': pack.id}
                                new_ids_write = {'lot_id': new_lot_id}
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
    vehical_registration_no = fields.Char(string="Vehicka Reg. No")
    basic_of_freight = fields.Selection([('to_pay', 'To Pay'), ('paid', 'Paid')], 'Basic Of Freight', default='')
    road_permit_no = fields.Char(string="Road Permit No")
    delivery_type = fields.Selection([('door_delivery', 'DOOR DELIVERY'), ('godown_delivery', 'GODOWN DELIVERY')], 'Delivery Type', default='door_delivery')
    dc_mode = fields.Selection([('returnable', 'Returnable'), ('non_returnable', 'Non-Returnable')], 'Delivery Mode')


class TransporterName(models.Model):
    _name = "transporter.name"

    """ Newly added class to reate entries for transporter used on DC form"""

    name = fields.Char(string="Name")
