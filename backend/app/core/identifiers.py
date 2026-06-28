"""
Identificadores del sistema.

- UUIDv7: claves primarias ordenables temporalmente (mejor localidad de índice
  que UUIDv4, sin exponer secuencias correlativas como los enteros autoincrement).
- public_slug: identificador público opaco para URLs (`/m/x8KfM9nQaR2vLpY7wZcH`).
  Nunca exponemos los UUID reales al exterior.

La generación de UUIDv7 sigue el borrador RFC 9562. Implementada en la capa de
aplicación para ser independiente de la versión de PostgreSQL.
"""
from __future__ import annotations

import os
import secrets
import time
import uuid

# Alfabeto sin caracteres ambiguos (0/O, 1/l/I) para slugs legibles.
_SLUG_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_DEFAULT_SLUG_LENGTH = 20


def uuid7() -> uuid.UUID:
    """
    Genera un UUID versión 7 (timestamp Unix en ms + bits aleatorios).

    Layout (128 bits):
      - 48 bits: timestamp Unix en milisegundos
      -  4 bits: versión (0b0111 = 7)
      - 12 bits: aleatorios (rand_a)
      -  2 bits: variante (0b10)
      - 62 bits: aleatorios (rand_b)
    """
    unix_ms = int(time.time() * 1000)
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)

    value = (unix_ms & 0xFFFFFFFFFFFF) << 80
    value |= 0x7 << 76          # versión
    value |= rand_a << 64
    value |= 0b10 << 62         # variante
    value |= rand_b
    return uuid.UUID(int=value)


def uuid7_str() -> str:
    return str(uuid7())


def generate_public_slug(length: int = _DEFAULT_SLUG_LENGTH) -> str:
    """
    Genera un slug público opaco, criptográficamente aleatorio.

    Ejemplo: `x8KfM9nQaR2vLpY7wZcH`
    Espacio de claves con 20 caracteres ≈ 56^20 ≈ 10^35 combinaciones:
    imposible de enumerar por fuerza bruta.
    """
    return "".join(secrets.choice(_SLUG_ALPHABET) for _ in range(length))


def generate_token(n_bytes: int = 32) -> str:
    """Token URL-safe para verificación de email, reset de contraseña, etc."""
    return secrets.token_urlsafe(n_bytes)


def constant_time_compare(a: str, b: str) -> bool:
    """Comparación en tiempo constante para tokens (anti timing-attack)."""
    return secrets.compare_digest(a.encode(), b.encode())
