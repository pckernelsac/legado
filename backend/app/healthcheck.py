"""Health check para Docker (`python -m app.healthcheck`). Exit 0 = sano."""
from __future__ import annotations

import sys
import urllib.request


def main() -> int:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5) as resp:
            return 0 if resp.status == 200 else 1
    except Exception:  # noqa: BLE001
        return 1


if __name__ == "__main__":
    sys.exit(main())
