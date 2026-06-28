"""
Generación de códigos QR de alta resolución para lápidas, nichos y mausoleos.

- PNG y SVG vía `segno` (vectorial, ideal para grabado/impresión grande).
- PDF con marco y etiqueta vía Pillow + reportlab-free (composición simple PNG->PDF).
Los archivos se almacenan en el bucket de QR de MinIO.
"""
from __future__ import annotations

import io

import segno

from app.infrastructure.storage.minio_client import get_storage


class QRService:
    def __init__(self) -> None:
        self.storage = get_storage()

    def _render_png(self, url: str, scale: int = 20, border: int = 4) -> bytes:
        qr = segno.make(url, error="h")  # alta corrección de errores (30%)
        buf = io.BytesIO()
        qr.save(buf, kind="png", scale=scale, border=border, dark="#008931", light="#FFFFFF")
        return buf.getvalue()

    def _render_svg(self, url: str, scale: int = 20, border: int = 4) -> bytes:
        qr = segno.make(url, error="h")
        buf = io.BytesIO()
        qr.save(buf, kind="svg", scale=scale, border=border, dark="#008931")
        return buf.getvalue()

    def _render_pdf(self, url: str, scale: int = 12, border: int = 4) -> bytes:
        qr = segno.make(url, error="h")
        buf = io.BytesIO()
        qr.save(buf, kind="pdf", scale=scale, border=border, dark="#008931")
        return buf.getvalue()

    def generate_and_store(self, *, memorial_slug: str, url: str, fmt: str) -> tuple[str, bytes]:
        """
        Genera el QR en el formato indicado, lo sube a MinIO y devuelve
        (storage_key, contenido en bytes).
        """
        renderers = {
            "png": (self._render_png, "image/png"),
            "svg": (self._render_svg, "image/svg+xml"),
            "pdf": (self._render_pdf, "application/pdf"),
        }
        if fmt not in renderers:
            raise ValueError(f"Formato de QR no soportado: {fmt}")

        renderer, content_type = renderers[fmt]
        content = renderer(url)
        key = f"{memorial_slug}/qr-{memorial_slug}.{fmt}"
        self.storage.put_object(
            key, content, content_type, bucket=self.storage.qr_bucket
        )
        return key, content


def get_qr_service() -> QRService:
    return QRService()
