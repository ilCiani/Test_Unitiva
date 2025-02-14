from odoo import models, fields

class MotivazioniOrdine(models.Model):
    _name = "motivazioni.ordine"
    _description = "Motivazioni Ordine"

    nome = fields.Char(string="Motivazione", required=True)
    stato_ordine = fields.Selection([
        ('da_validare', "Da Validare"),
        ('da_revisionare', "Da Revisionare"),
        ('da_confermare', "Da Confermare"),
        ('confermato', "Confermato"),
        ('sospeso', "Sospeso"),
        ('annullato', "Annullato"),
    ], string="Stato ordine", required=True)


    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.nome))
        return result