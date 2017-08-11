# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import UserError, AccessError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    # This field allow to use product weight in Sale order Line
    is_weight_applicable = fields.Boolean(string="Allow To Use Weight")

    raw_size = fields.Char(string="Size (Raw)")
    finished_size = fields.Char(string="Size (Finished)")
    material = fields.Char(string="Material")
    machine_drawing_no = fields.Char(string="Machine Drawing No")
    machine_drawing_no_file = fields.Binary(string="Machine Drawing File")
    machine_filename = fields.Char('Machine File name', store=True)
    casting_drawing_no = fields.Char(string="Casting Drawing No")
    casting_drawing_no_file = fields.Binary(string="Casting Drawing File")
    casting_filename = fields.Char('Casting File name', store=True)
    od = fields.Char(string="OD (mm)")
    l = fields.Char(string="L (mm)")
    b_id = fields.Char(string="ID (mm)")

    @api.multi
    def _create_attachment_for_machine(self):
        """
            Create attachment from uploaded files
            for Machine Drawing File
        """
        attachment_obj = self.env['ir.attachment']
        if self.machine_filename:
            split_file_name = self.machine_filename.split('.')
            print split_file_name[-1],'---------split_file_name'
            conct_file_name = split_file_name[-2] + '_' + self.machine_drawing_no + '.' + split_file_name[-1]
            ir_attachment_vals = {
                'name': conct_file_name,#self.machine_filename + '-' + self.machine_drawing_no,
                'type': 'binary',
                'datas_fname': self.machine_filename,
                'datas': self.machine_drawing_no_file,
                'res_model': 'product.template',
                'res_id': self.id,
                'res_name': self.name,
            }
            attachment_id = attachment_obj.create(ir_attachment_vals)
            return attachment_id

    @api.multi
    def _create_attachment_for_casting(self):
        """
            Create attachment from uploaded files
            For Casting Drawing File
        """
        attachment_obj = self.env['ir.attachment']
        f_name = ''
        if self.casting_filename:
            print self.casting_filename,'-------self.casting_filename'
            split_file_name = self.casting_filename.split('.')
            print len(split_file_name),'---split_file_name'
            # jkjdfkjdjjjkkkkk
            # print split_file_name[-2],'---------split_file_name'
            # for i in range(len(split_file_name)-1)
            #     f_name =
            conct_file_name = split_file_name[-2] + '_' + self.casting_drawing_no + '.' + split_file_name[-1]
            print conct_file_name,'----------conct_file_name'
            ir_attachment_vals = {
                'name': conct_file_name, #self.casting_filename + '-' + self.casting_drawing_no,
                'type': 'binary',
                'datas_fname': self.casting_filename,
                'datas': self.casting_drawing_no_file,
                'res_model': 'product.template',
                'res_id': self.id,
                'res_name': self.name,
            }
            attachment_id = attachment_obj.create(ir_attachment_vals)
            return attachment_id

    @api.multi
    def write(self, vals):
        attachment_obj = self.env['ir.attachment']

        res = super(ProductTemplate, self).write(vals)

        """ Logic for to create ir.attachment from uploaded file"""
        if vals and 'machine_drawing_no_file' in vals:
            ## Create attachment For Machine Drawing
            if not self.machine_drawing_no:
                raise UserError(_('Please Enter Machine Drawing No'))
            attachment_id = self._create_attachment_for_machine()
            ## Assign new name to uploaded file e.g Machine No + file name
            if attachment_id:
                self.machine_filename = attachment_id.name

        ## Logic for deleting attachment when file is deleted
        if vals and 'machine_drawing_no_file' in vals and vals.get('machine_drawing_no_file') == False:
            ## Delete attachment object in no file name is there
            attachment_ids = attachment_obj.search([('res_id','=',self.id),('res_model','=','product.template')])
            for attachment_id in attachment_ids:
                ## AS we are considering machine_drawing_no and casting_drawing_no name
                ## will be different always
                res = self.machine_drawing_no in attachment_id.name
                if res:
                    attachment_id.unlink()

        if vals and 'casting_drawing_no_file' in vals:
            ## Create attachment For Casting Drawing
            if not self.casting_drawing_no:
                raise UserError(_('Please Enter Catsting Drawing No'))
            attachment_id = self._create_attachment_for_casting()
            ## Assign new name to uploaded file e.g Casting No + file name
            if attachment_id:
                self.casting_filename = attachment_id.name

        ## Logic for deleting attachment when file is deleted
        if vals and 'casting_drawing_no_file' in vals and vals.get('casting_drawing_no_file') == False:
            ## Delete attachment object in no file name is there
            attachment_ids = attachment_obj.search([('res_id','=',self.id),('res_model','=','product.template')])
            for attachment_id in attachment_ids:
                ## AS we are considering machine_drawing_no and casting_drawing_no name
                ## will be different always
                res = self.casting_drawing_no in attachment_id.name
                if res:
                    attachment_id.unlink()

        return res

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if vals and 'machine_drawing_no_file' in vals and vals['machine_drawing_no_file'] != False:
            ## Create attachment For Machine Drawing
            if not vals['machine_drawing_no']:
                raise UserError(_('Please Enter Machine Drawing No'))
            attachment_id = res._create_attachment_for_machine()
            ## Assign new name to uploaded file e.g Machine No + file name
            res.machine_filename = attachment_id.name
        if vals and 'casting_drawing_no_file' in vals and vals['casting_drawing_no_file'] != False:
            ## Create attachment For Casting Drawing
            if vals['casting_drawing_no'] == False:
                raise UserError(_('Please Enter Casting Drawing No'))
            attachment_id = res._create_attachment_for_casting()
            ## Assign new name to uploaded file e.g Casting No + file name
            res.casting_filename = attachment_id.name
        return res
