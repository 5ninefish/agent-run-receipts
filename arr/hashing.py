from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Union

BytesLike = Union[bytes, bytearray]


def sha256_bytes(data: BytesLike) -> str:
    return hashlib.sha256(bytes(data)).hexdigest()


def sha256_file(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return sha256_bytes(data), len(data)


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_json(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def receipt_digest(receipt: dict) -> str:
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    return sha256_bytes(canonical_json(body))
