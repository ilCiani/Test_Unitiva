from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Persona
    referente_interno = fields.Boolean(string="Referente Interno")
    rappresentante_legale = fields.Boolean(string="Rappresentante Legale")
    data_nascita = fields.Date(string="Data di Nascita")
    luogo_nascita = fields.Char(string="Luogo di Nascita")
    tipo_documento = fields.Selection([
        ('ci', _("Carta d'Identità")),
        ('patente', _("Patente")),
        ('passaporto', _("Passaporto")),
    ], string="Tipo Documento")
    numero_documento = fields.Char(string="Numero Documento")
    data_emissione_documento = fields.Date(string="Data Emissione Documento")
    scadenza_documento = fields.Date(string="Scadenza Documento")

    # Azienda
    categoria_merceologica_id = fields.Many2one('ciani.unitiva.categoria', string="Categoria Merceologica")
    progressivo_cliente = fields.Char(string="Progressivo Cliente", readonly=True, copy=False, default=lambda self: _('New'))
    referente_interno_id = fields.Many2one(
        'res.partner',
        string="Referente Interno Aziendale",
        domain="[('is_company', '=', False), ('referente_interno', '=', True)]"
    )
    rappresentante_legale_id = fields.Many2one(
        'res.partner',
        string="Rappresentante Legale Aziendale",
        domain="[('is_company', '=', False), ('rappresentante_legale', '=', True)]"
    )

    # Flusso
    approvazione_stato = fields.Selection([
        ('da_approvare', _("Da Approvare")),
        ('approvato', _("Approvato")),
    ], string="Stato Approvazione", default='da_approvare')

    @api.constrains('approvazione_stato', 'referente_interno_id', 'rappresentante_legale_id')
    def _controlla_approvazione_referenti(self):
        for rec in self:
            if rec.is_company and rec.approvazione_stato == 'approvato' and not (rec.referente_interno_id or rec.rappresentante_legale_id):
                raise UserError(_("Per approvare un contatto di tipo Azienda occorre specificare almeno un Referente Interno o un Rappresentante Legale. Grazie!"))

    def bottone_approva(self):
        for rec in self:
            if rec.is_company and not (rec.referente_interno_id or rec.rappresentante_legale_id):
                return {
                    'warning': {
                        'title': _("Attenzione"),
                        'message': _("Impossibile approvare il contatto: specificare almeno un Referente Interno o un Rappresentante Legale. Grazie!")
                    }
                }
            rec.approvazione_stato = 'approvato'
        return True

    def bottone_reimposta(self):
        for rec in self:
            rec.approvazione_stato = 'da_approvare'
        return True

    @api.model
    def create(self, vals):
        if vals.get('is_company') and vals.get('progressivo_cliente', _('New')) == _('New'):
            vals['progressivo_cliente'] = self.env['ir.sequence'].next_by_code('res.partner.client.progressivo') or _('New')
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        # Blocca la modifica di campi se il contatto è approvato
        campi_bloccati = ['street', 'street2', 'city', 'zip', 'state_id', 'country_id', 'vat']
        for rec in self:
            if rec.approvazione_stato == 'approvato' and any(campo in vals for campo in campi_bloccati):
                raise UserError(_("Non è possibile modificare indirizzo o VAT di un contatto già approvato."))
        return super(ResPartner, self).write(vals)

    @api.constrains('vat')
    def _controlla_vat_univoco(self):
        for rec in self:
            if rec.vat:
                duplicati = self.search([('vat', '=', rec.vat), ('id', '!=', rec.id)])
                if duplicati:
                    raise UserError(_("Esiste già un contatto con lo stesso VAT."))
                
    @api.constrains('data_emissione_documento', 'scadenza_documento')
    def _controlla_data_documento(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.data_emissione_documento and rec.data_emissione_documento > today:
                raise UserError(_("Documento non ancora emesso. Sei sicuro?"))

            if rec.scadenza_documento and rec.scadenza_documento <= today:
                raise UserError(_("Documento scaduto!"))