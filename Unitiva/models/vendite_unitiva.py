from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class VenditeUnitiva(models.Model):
    _inherit = "sale.order"

    stato_personalizzato = fields.Selection([
        ('da_validare', "Da Validare"),
        ('da_revisionare', "Da Revisionare"),
        ('da_confermare', "Da Confermare"),
        ('confermato', "Confermato"),
        ('sospeso', "Sospeso"),
        ('annullato', "Annullato"),
    ], string="Stato", default='da_validare', tracking=True)

    stato_precedente = fields.Selection([
        ('da_validare', "Da Validare"),
        ('da_revisionare', "Da Revisionare"),
        ('da_confermare', "Da Confermare"),
        ('confermato', "Confermato"),
    ], string="Stato Precedente", readonly=True)



    rinnovo_automatico = fields.Boolean(string="Rinnovo Automatico")
    piano_rinnovo_id = fields.Many2one(
        comodel_name="vendite.unitiva.piano_rinnovo",
        string="Piano di Rinnovo"
    )
    motivazione_id = fields.Many2one("motivazioni.ordine", string="Motivazione", help="Seleziona la motivazione relativa a questo ordine")
    

    # Campi Welcom Call
    esito_welcome_call = fields.Selection([
        ('ok', "OK"),
        ('irreperibile', "Irreperibile"),
        ('ko', "KO"),
    ], string="Esito Welcome Call")

    appunti_welcome_call = fields.Text(string="Appunti Welcome Call")

    deadline_recesso = fields.Date(string="Deadline Recesso")




    def open_wizard_cambio_stato(self):
        return {
            "name": "Cambio Stato Ordine",
            "type": "ir.actions.act_window",
            "res_model": "wizard.cambio.stato.ordine",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_id": self.id,
                "default_motivazione_id": self.motivazione_id.id,
                "default_note": self.note,
                "default_state_to_set": self.stato_personalizzato,
            },
        }


    def bottone_cambia_stato(self):
        transizioni = {
            'da_validare': 'da_revisionare',
            'da_revisionare': 'da_confermare',
            'da_confermare': 'confermato',
            'confermato': 'annullato', 
        }
        if self.stato_personalizzato in transizioni:
            self.stato_personalizzato = transizioni[self.stato_personalizzato]

    def bottone_sospendi_riattiva(self):
        if self.stato_personalizzato == 'sospeso':
            self.stato_personalizzato = self.stato_precedente or 'da_validare'
        else:
            self.stato_precedente = self.stato_personalizzato
            self.stato_personalizzato = 'sospeso'

    # Metodo validazione massiva
    def action_validate_orders(self):
        if not self:
            return
        
        stati_distinti = self.mapped("stato_personalizzato")

        if len(set(stati_distinti)) > 1:
            raise UserError("Tutti gli ordini selezionati devono avere lo stesso stato per essere validati.")

        self.write({"stato_personalizzato": "da_confermare"})


    # Funzioni Welcome Call
    def welcome_call_annulla_ordine(self):
        self.write({"stato_personalizzato": "annullato"})

    def welcome_call_invia_preventivo(self):
        if self.esito_welcome_call == 'ko':
            raise UserError("Mi dispiace, Esito Welcome Call è 'KO'.")

        view_id = self.env.ref('unitiva.view_wizard_invia_preventivo_form').id
        return {
            'name': 'Invia Preventivo',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.invia.preventivo',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_attachment_id': self._get_default_pdf_attachment().id
            }
        }

    def _get_default_pdf_attachment(self):
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'sale.order'),
            ('res_id', '=', self.id),
            ('mimetype', 'ilike', 'pdf')
        ], limit=1)
        return attachment


    def welcome_call_conferma_ordine(self):
        if self.esito_welcome_call == 'ko':
            raise UserError("Non puoi confermare il preventivo se l'Esito Welcome Call è 'KO'.")

        self.write({
            "stato_personalizzato": "confermato",
            "deadline_recesso": fields.Date.today() + timedelta(days=14),
        })  




class PianoRinnovo(models.Model):
    _name = "vendite.unitiva.piano_rinnovo"
    _description = "Piano di Rinnovo"

    nome = fields.Char(string="Nome", required=True)
    numero = fields.Integer(string="Numero", required=True)
    tipo_intervallo = fields.Selection(
        selection=[
            ("giorni", "Giorni"),
            ("mesi", "Mesi"),
            ("anni", "Anni"),
        ],
        string="Tipo Intervallo",
        required=True,
    )