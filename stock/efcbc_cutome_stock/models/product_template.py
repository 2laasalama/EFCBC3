# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_asset = fields.Boolean(string='أصل')
    brand_id = fields.Many2one('product.brand',string='الماركة')
    manufacture_company_id = fields.Many2one('product.manufacture.company',string='الشركه المصنعه')
    model_id = fields.Many2one('product.model',string='الموديل')

class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char(required=1)

class ProductModel(models.Model):
    _name = 'product.model'

    name = fields.Char(required=1)

class ProductManufactureCompany(models.Model):
    _name = 'product.manufacture.company'

    name = fields.Char(required=1)



