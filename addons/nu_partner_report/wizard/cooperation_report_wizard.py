import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError

REPORT_XMLID = 'nu_partner_report.action_report_partner_cooperation'


class CooperationReportWizard(models.TransientModel):
    _name = 'nu.cooperation.report.wizard'
    _description = 'Cooperation Report: download or send'

    partner_id = fields.Many2one('res.partner', required=True, readonly=True)
    is_person = fields.Boolean(compute='_compute_scope')
    scope_label = fields.Char(compute='_compute_scope')
    company_partner_id = fields.Many2one('res.partner', compute='_compute_scope')

    email_to = fields.Char(
        string='Send to',
        help='Comma-separated addresses. Leave empty to only download.',
    )
    subject = fields.Char()
    body = fields.Html(sanitize_style=True)

    @api.depends('partner_id')
    def _compute_scope(self):
        for wiz in self:
            partner = wiz.partner_id
            person = partner and partner._is_contact_person()
            wiz.is_person = bool(person)
            wiz.company_partner_id = partner._cooperation_root() if partner else False
            if person:
                wiz.scope_label = _(
                    'Contact report for %(name)s — includes the cooperation '
                    'history of %(company)s.',
                    name=partner.name,
                    company=wiz.company_partner_id.name or _('their organisation'),
                )
            else:
                wiz.scope_label = _(
                    'Full cooperation report for %(name)s.', name=partner.name or ''
                )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Prefill subject/body, and default the recipient to the *current user*.

        Deliberately NOT the partner's own address: this report is an internal
        document, and prefilling a real external company address makes it one
        careless click to send NU's internal pipeline data to that company.
        Whoever wants to send it outward can type the address on purpose.
        """
        for wiz in self:
            partner = wiz.partner_id
            if not partner:
                continue
            wiz.email_to = self.env.user.email or ''
            wiz.subject = _('Cooperation report — %(name)s', name=partner.name)
            wiz.body = _(
                '<p>Dear colleague,</p>'
                '<p>Please find attached the cooperation report for '
                '<strong>%(name)s</strong>.</p>'
                '<p>Kind regards,<br/>%(sender)s<br/>%(company)s</p>',
                name=partner.name,
                sender=self.env.user.name,
                company=self.env.company.name,
            )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _render_pdf(self):
        self.ensure_one()
        report = self.env.ref(REPORT_XMLID)
        pdf, _ext = self.env['ir.actions.report']._render_qweb_pdf(
            report.report_name, res_ids=self.partner_id.ids
        )
        return pdf

    def _filename(self):
        self.ensure_one()
        safe = (self.partner_id.name or 'partner').replace('/', '-')
        return f'Cooperation Report - {safe}.pdf'

    def action_download(self):
        """Hand the PDF straight to the browser."""
        self.ensure_one()
        return self.env.ref(REPORT_XMLID).report_action(self.partner_id)

    def action_preview(self):
        """Open the report as a web page.

        Useful because it skips PDF rendering entirely and so appears
        instantly, where producing the PDF itself takes a couple of seconds.
        """
        self.ensure_one()
        report = self.env.ref(REPORT_XMLID)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f'/report/html/{report.report_name}/{self.partner_id.id}',
        }

    def action_send_email(self):
        """Email the PDF as an attachment."""
        self.ensure_one()
        if not self.email_to:
            raise UserError(_('Enter at least one recipient address first.'))
        if not self.env['ir.mail_server'].sudo().search_count([]):
            raise UserError(_(
                'No outgoing mail server is configured, so the report cannot be '
                'sent. Configure one under Settings > Technical > Email, or use '
                'Download instead.'
            ))

        attachment = self.env['ir.attachment'].create({
            'name': self._filename(),
            'datas': base64.b64encode(self._render_pdf()),
            'mimetype': 'application/pdf',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
        })

        mail = self.env['mail.mail'].sudo().create({
            'subject': self.subject or _('Cooperation report'),
            'body_html': self.body or '',
            'email_to': self.email_to,
            'email_from': self.env.user.email_formatted or self.env.company.email,
            'attachment_ids': [(6, 0, attachment.ids)],
        })
        mail.send(raise_exception=True)

        # Leave a trace on the partner so the send is part of the history.
        self.partner_id.message_post(
            body=_('Cooperation report sent to %(to)s.', to=self.email_to),
            attachment_ids=attachment.ids,
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Report sent'),
                'message': _('Sent to %(to)s.', to=self.email_to),
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
