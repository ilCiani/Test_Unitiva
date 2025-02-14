from odoo import models, fields

class CategoriaMerceologica(models.Model):
    _name = 'ciani.unitiva.categoria'
    _description = 'Categoria Merceologica (Codici ATECO)'

    code = fields.Char(string='Codice ATECO', required=True)
    name = fields.Char(string='Descrizione', required=True)