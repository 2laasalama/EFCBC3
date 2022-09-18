# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
from datetime import datetime, timedelta
from itertools import product as cartesian_product
from collections import defaultdict

from odoo import models, api, fields, _
from odoo.tools import populate, groupby


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def action_view_inventory_assets(self):
        """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
        self = self._set_view_context()
        self._quant_tasks()

        ctx = dict(self.env.context or {})
        ctx['no_at_date'] = True
        if self.user_has_groups('stock.group_stock_user') and not self.user_has_groups('stock.group_stock_manager'):
            ctx['search_default_my_count'] = True
        action = {
            'name': _('Inventory Adjustments'),
            'view_mode': 'list',
            'view_id': self.env.ref('stock.view_stock_quant_tree_inventory_editable').id,
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('location_id.usage', 'in', ['internal', 'transit']),'|',
                       ('product_id.is_asset', '=', True),
                       ('location_id.fixed_assets', '=', True)],
            'help': """
                   <p class="o_view_nocontent_smiling_face">
                       {}
                   </p><p>
                       {} <span class="fa fa-long-arrow-right"/> {}</p>
                   """.format(_('Your stock is currently empty'),
                              _('Press the CREATE button to define quantity for each product in your stock or import them from a spreadsheet throughout Favorites'),
                              _('Import')),
        }
        return action
