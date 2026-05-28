"""File-upload magic-byte validation.

Checks that the actual file content matches the declared MIME type.
This prevents uploading a malicious file (e.g. an executable) while
claiming it is an image by spoofing the Content-Type header.
"""
from fastapi import HTTPException, status

# Expected leading byte sequences per MIME type.
# A list value means any of the listed headers is acceptable.
_MAGIC: dict[str, bytes | list[bytes]] = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/gif": [b"GIF87a", b"GIF89a"],
    "image/webp": b"RIFF",          # special-cased below: also checks bytes 8-12
    "application/pdf": b"%PDF",
    # Legacy Office (OLE2 Compound Document)
    "application/msword": b"\xd0\xcf\x11\xe0",
    "application/vnd.ms-excel": b"\xd0\xcf\x11\xe0",
    # Modern Office (OOXML = ZIP)
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": b"PK\x03\x04",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": b"PK\x03\x04",
}


def verify_magic_bytes(content: bytes, declared_mime: str) -> bool:
    """Return True if *content* starts with the expected header for *declared_mime*."""
    magic = _MAGIC.get(declared_mime)
    if magic is None:
        return False  # unknown type — reject

    if declared_mime == "image/webp":
        return (
            len(content) >= 12
            and content[:4] == b"RIFF"
            and content[8:12] == b"WEBP"
        )

    if isinstance(magic, list):
        return any(content.startswith(m) for m in magic)
    return content.startswith(magic)


def assert_magic_bytes(content: bytes, declared_mime: str) -> None:
    """Raise HTTP 415 if file content does not match the declared MIME type."""
    if not verify_magic_bytes(content, declared_mime):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"File content does not match the declared type '{declared_mime}'. "
                "Please upload an unmodified file."
            ),
        )
