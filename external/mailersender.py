import os

from mailersend import emails

_API_KEY = os.getenv("MAILERSEND_API_KEY", "")
_FROM_EMAIL = os.getenv("MAILERSEND_FROM_EMAIL", "noreply@vigil.ai")
_FROM_NAME = os.getenv("MAILERSEND_FROM_NAME", "Vigil.AI")


def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    text_content: str | None = None,
) -> dict:
    mailer = emails.NewEmail(_API_KEY)

    mail_body = {}
    mailer.set_mail_from({"name": _FROM_NAME, "email": _FROM_EMAIL}, mail_body)
    mailer.set_mail_to([{"name": to_name, "email": to_email}], mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(html_content, mail_body)
    if text_content:
        mailer.set_plaintext_content(text_content, mail_body)

    return mailer.send(mail_body)


def send_bulk(recipients: list[dict], subject: str, html_content: str, text_content: str | None = None) -> list[dict]:
    return [
        send_email(
            to_email=r["email"],
            to_name=r.get("name", r["email"]),
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )
        for r in recipients
    ]
