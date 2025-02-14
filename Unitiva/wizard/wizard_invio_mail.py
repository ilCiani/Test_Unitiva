from odoo import models, fields, api
from odoo.exceptions import UserError

class WizardInviaPreventivo(models.TransientModel):
    _name = 'wizard.invia.preventivo'
    _description = 'Wizard per inviare Preventivo'

    sale_order_id = fields.Many2one('sale.order', string="Ordine", required=True)
    partner_id = fields.Many2one('res.partner', string="Destinatario", required=True)
    partner_email = fields.Char(string="Email del Cliente", related="partner_id.email", readonly=True)
    attachment_id = fields.Many2one('ir.attachment', string="Allegato del Preventivo")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardInviaPreventivo, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['sale.order'].browse(active_id)
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id),
                ('mimetype', 'ilike', 'pdf'),
                ('name', 'ilike', order.partner_id.name)
            ], limit=1)
            res.update({
                'sale_order_id': order.id,
                'partner_id': order.partner_id.id,
                'attachment_id': attachment.id if attachment else False
            })
        return res

    def action_send_email(self):
        self.ensure_one()
        if not self.attachment_id:
            raise UserError("Nessun PDF allegato disponibile per l'invio.")

        mail_values = {
            'subject': f"Preventivo per {self.partner_id.name}",
            'email_from': self.env.user.email or 'gianmarco.ciani@gmail.com',
            'email_to': self.partner_email,
            'body_html': f"<p>Salve,</p><p>In allegato troverà il preventivo.</p>",
            'attachment_ids': [(6, 0, [self.attachment_id.id])] if self.attachment_id else []
        }
        mail_id = self.env['mail.mail'].create(mail_values)
        mail_id.send()

        return {
            'type': 'ir.actions.act_window_close'
        }