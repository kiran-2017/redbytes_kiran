# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    """Inherit this class for adding new fields on company form to print on TAX INVOICE REPORT"""

    #Add cst on company view
    declaration = fields.Text(string="Declaration")
