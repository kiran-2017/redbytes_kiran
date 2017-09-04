# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_vat_tin = fields.Char(string="VAT TIN")
    ## Add new fields for GST
    place_of_supply = fields.Char(string="Place of Supply/State code")
    partner_gstin = fields.Char(string="GSTIN")


    @api.multi
    def write(self, vals):
        """ Logic for to assign vat tin and GSTIN to partners all child contacts"""
        if vals and 'partner_vat_tin' in vals:
            for child in self.child_ids:
                child.partner_vat_tin = vals['partner_vat_tin']
        ## Hide not required to assign GSTIN on child contacts
        ## Keep for future
        # if vals and 'partner_gstin' in vals:
        #     for child in self.child_ids:
        #         child.partner_gstin = vals['partner_gstin']

        if vals and 'partner_gstin' in vals:
            """
                Assign state code from GSTIN entered
                1st 2 digit should be assign to state code
            """
            partner_gstin = str(vals.get('partner_gstin'))
            gstin_list = [i for i in str(partner_gstin)]
            if gstin_list:
                vals['place_of_supply'] = gstin_list[0] + gstin_list[1]

        res = super(ResPartner, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        """
            Assign state code from GSTIN entered
            1st 2 digit should be assign to state code
        """
        if vals and 'partner_gstin' in vals:
            """
                Assign state code from GSTIN entered
                1st 2 digit should be assign to state code
            """
            partner_gstin = str(vals.get('partner_gstin'))
            gstin_list = [i for i in str(partner_gstin)]
            if gstin_list:
                vals['place_of_supply'] = gstin_list[0] + gstin_list[1]
        res = super(ResPartner, self).create(vals)
        return res
