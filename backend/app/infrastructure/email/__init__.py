"""Infraestructura de email transaccional."""
from app.infrastructure.email.sender import render_email, send_email_smtp

__all__ = ["render_email", "send_email_smtp"]
