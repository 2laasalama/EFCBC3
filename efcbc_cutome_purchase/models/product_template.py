# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    main_type = fields.Selection(
        string='النوع',
        selection=[('supply', 'توريدات'),
                   ('work', 'أعمال')])

    # is_asset = fields.Boolean()
