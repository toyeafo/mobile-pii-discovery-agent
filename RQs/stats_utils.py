import re
from typing import Any, Dict, List, Optional

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _collapse_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _dedupe_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for v in values:
        if v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out

def normalize_email(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = re.sub(r"^mailto:\s*", "", s, flags=re.IGNORECASE).strip()
    s = _collapse_spaces(s.lower()).strip("<>")
    return s if _EMAIL_RE.match(s) else None

def normalize_phone_keep_all(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    digits = re.sub(r"\D", "", s)
    return digits or None

def normalize_username(value: Any) -> Optional[str]:
    """
    USERNAME: lowercase only (plus strip).
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return s.lower()

def normalize_person_name(value: Any) -> Optional[str]:
    """
    PERSON_NAME: lowercase + collapse spaces.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return _collapse_spaces(s.lower())

def normalize_postal_address(value: Any) -> Optional[str]:
    """
    POSTAL_ADDRESS: lowercase + collapse spaces + normalize comma spacing.
    """
    if value is None:
        return None
    s = _collapse_spaces(str(value)).lower()
    if not s:
        return None
    s = re.sub(r"\s*,\s*", ", ", s)
    s = _collapse_spaces(s)
    return s or None

def normalize_source_column(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = _collapse_spaces(str(value)).lower()
    return s or None

def normalize_pii_value(pii_type: str, value: Any) -> Optional[str]:
    t = (pii_type or "").strip().upper()
    if t == "EMAIL":
        return normalize_email(value)
    if t == "PHONE":
        return normalize_phone_keep_all(value)
    if t == "USERNAME":
        return normalize_username(value)
    if t == "PERSON_NAME":
        return normalize_person_name(value)
    if t == "POSTAL_ADDRESS":
        return normalize_postal_address(value)
    return None

def normalize_and_slim_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Output only:
      db_path, PII_type, PII, Num_of_PII, source_columns, Num_of_source_columns

    Also dedupes PII and source_columns and recalculates counts.
    """
    db_path = rec.get("db_path", "")
    pii_type = (rec.get("PII_type") or "").strip().upper()

    pii_list = rec.get("PII", [])
    if not isinstance(pii_list, list):
        pii_list = [pii_list] if pii_list is not None else []

    src_cols = rec.get("source_columns", [])
    if not isinstance(src_cols, list):
        src_cols = [src_cols] if src_cols is not None else []

    normalized_pii: List[str] = []
    for v in pii_list:
        nv = normalize_pii_value(pii_type, v)
        if nv is not None:
            normalized_pii.append(nv)
    normalized_pii = _dedupe_preserve_order(normalized_pii)

    normalized_src: List[str] = []
    for c in src_cols:
        nc = normalize_source_column(c)
        if nc is not None:
            normalized_src.append(nc)
    normalized_src = _dedupe_preserve_order(normalized_src)

    return {
        "db_path": db_path,
        "PII_type": pii_type,
        "PII": normalized_pii,
        "Num_of_PII": len(normalized_pii),
        "source_columns": normalized_src,
        "Num_of_source_columns": len(normalized_src),
    }