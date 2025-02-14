from odoo import models, fields, api

class WizardCambioStatoOrdine(models.TransientModel):
    _name = "wizard.cambio.stato.ordine"
    _description = "Wizard per Cambio Stato Ordine"

    sale_order_id = fields.Many2one("sale.order", string="Ordine di Vendita", required=True, readonly=True)
    motivazione_id = fields.Many2one("motivazioni.ordine", string="Motivazione", required=False)
    note = fields.Text(string="Note")
    state_to_set = fields.Selection([
        ('da_validare', 'Da Validare'),
        ('da_revisionare', 'Da Revisionare'),
        ('da_confermare', 'Da Confermare'),
        ('confermato', 'Confermato'),
        ('sospeso', 'Sospeso'),
        ('annullato', 'Annullato'),
    ], string="Nuovo Stato", readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(WizardCambioStatoOrdine, self).default_get(fields)
        if self.env.context.get("default_sale_order_id"):
            res["sale_order_id"] = self.env.context["default_sale_order_id"]
        if self.env.context.get("default_state_to_set"):
            res["state_to_set"] = self.env.context["default_state_to_set"]
        return res

    def conferma_cambio_stato(self):
        self.ensure_one()
        if self.sale_order_id:
            self.sale_order_id.write({
                "stato_personalizzato": self.state_to_set,
                "motivazione_id": self.motivazione_id.id if self.motivazione_id else False,
                "note": self.note if self.note else "",
            })
        return {"type": "ir.actions.act_window_close"}