# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    portal_available = fields.Boolean()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    portal_available = fields.Boolean(related='product_tmpl_id.portal_available', store=True)


class InheritHrEmployee(models.Model):
    _inherit = 'hr.employee'

    user_id2 = fields.Many2one('res.users', string='User')

