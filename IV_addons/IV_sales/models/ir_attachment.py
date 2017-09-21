# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    so_doc_type = fields.Char(string="Document Type")
