# -*- coding: utf-8 -*-

from odoo import models, fields


class res_company(models.Model):
    _inherit = "res.company"


    executive_secretariat_image = fields.Binary('نموذج الامضاء الخاصه برئيس امانه المشتريات والمخازن')
