"""
Envío de email transaccional vía SMTP.

- Si `SMTP_HOST` no está configurado (típico en desarrollo sin MailHog), no
  intenta conectar: registra el contenido en el log para poder copiar el enlace.
- Con `SMTP_HOST` definido, envía por SMTP usando STARTTLS si `SMTP_TLS=true`.
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def render_email(
    *,
    title: str,
    intro: str,
    cta_label: str | None = None,
    cta_url: str | None = None,
    outro: str | None = None,
) -> str:
    """Envuelve el contenido en una plantilla HTML branded de Legado Eterno."""
    button = ""
    if cta_label and cta_url:
        button = f"""
        <tr><td style="padding:8px 0 24px;">
          <a href="{cta_url}" style="display:inline-block;background:#008931;color:#ffffff;
             text-decoration:none;font-weight:600;padding:12px 28px;border-radius:10px;font-size:15px;">
            {cta_label}
          </a>
        </td></tr>
        <tr><td style="padding:0 0 8px;color:#6B7280;font-size:13px;">
          Si el botón no funciona, copia este enlace:<br>
          <a href="{cta_url}" style="color:#006D27;word-break:break-all;">{cta_url}</a>
        </td></tr>
        """
    outro_html = (
        f'<tr><td style="padding:16px 0 0;color:#6B7280;font-size:14px;">{outro}</td></tr>'
        if outro
        else ""
    )
    return f"""\
<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#FAFAFA;font-family:Inter,Segoe UI,system-ui,sans-serif;color:#111827;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#FAFAFA;padding:32px 16px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="max-width:520px;background:#ffffff;border:1px solid #E5E7EB;border-radius:16px;padding:32px;">
        <tr><td style="padding-bottom:8px;font-size:20px;font-weight:700;color:#008931;">
          🕊️ Legado Eterno
        </td></tr>
        <tr><td style="padding:8px 0 4px;font-size:22px;font-weight:700;">{title}</td></tr>
        <tr><td style="padding:8px 0 16px;color:#374151;font-size:15px;line-height:1.6;">{intro}</td></tr>
        {button}
        {outro_html}
        <tr><td style="padding-top:24px;border-top:1px solid #E5E7EB;color:#9CA3AF;font-size:12px;">
          Recibiste este correo porque tienes una cuenta en Legado Eterno.
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def send_email_smtp(to: str, subject: str, html_body: str) -> bool:
    """
    Envía un email. Devuelve True si se envió por SMTP, False si solo se registró
    (SMTP no configurado). Lanza la excepción si SMTP está configurado pero falla.
    """
    if not settings.SMTP_HOST:
        logger.warning(
            "smtp_not_configured", to=to, subject=subject,
            note="Email no enviado (SMTP_HOST vacío). Contenido en log para dev.",
        )
        logger.info("email_preview", to=to, subject=subject, body=html_body)
        return False

    msg = EmailMessage()
    msg["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(
        "Tu cliente no soporta HTML. Abre este correo en un lector compatible."
    )
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        if settings.SMTP_TLS:
            smtp.starttls()
        if settings.SMTP_USER:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)

    logger.info("email_sent", to=to, subject=subject)
    return True
