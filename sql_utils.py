import re
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import yaml
import importlib.util
from typing import List, Tuple

def extract_tables_with_aliases(select_sql: str) -> dict[str, str]:
    """
    Returns mapping alias_or_table -> real_table
    Example: FROM messages m JOIN contacts c -> {"m":"messages","messages":"messages","c":"contacts","contacts":"contacts"}
    """
    TABLE_TOKEN = re.compile(
    r'\b(?:FROM|JOIN)\s+("?[A-Za-z_][A-Za-z0-9_]*"?)'
    r'(?:\s+(?:AS\s+)?("?[A-Za-z_][A-Za-z0-9_]*"?))?',
    re.IGNORECASE
    )
    m = {}
    for tbl, alias in TABLE_TOKEN.findall(select_sql):
        tbl = tbl.strip('"')
        if alias:
            alias = alias.strip('"')
            m[alias] = tbl
        m[tbl] = tbl
    return m

def extract_single_table(select_sql: str) -> str | None:
    m = extract_tables_with_aliases(select_sql)  # dict alias->table and table->table
    tables = sorted(set(m.values()))
    return tables[0] if len(tables) == 1 else None




def _bytes_to_display(b: bytes, max_len: int) -> str:
    # Try UTF-8 first (common for text stored as BLOB)
    _PRINTABLE_RE = re.compile(r"^[\x09\x0a\x0d\x20-\x7e]+$")  # tabs/newlines/spaces + printable ASCII
    try:
        s = b.decode("utf-8", errors="replace")
        s = s.strip()
        # If it is mostly printable, keep it
        if s and _PRINTABLE_RE.match(s[:min(len(s), 200)]):
            return s[:max_len] + ("..." if len(s) > max_len else "")
    except Exception:
        pass

    # Otherwise show hex preview (compact, honest)
    hx = b.hex()
    if len(hx) > max_len:
        return hx[:max_len] + "..."
    return hx

def rows_to_text(rows, limit=None, max_chars=500000, cell_max=1000):
    """
    Converts SQL rows to text with safety limits for LLM context.
    - limit: Max number of rows to process.
    - max_chars: Hard limit for the total string length.
    - cell_max: Max length for any single column value.
    """

    if not rows:
        return ""

    out = []
    target_rows = rows[:limit] if limit else rows

    for r in target_rows:
        if r is None:
            continue

        # Handle tuples/rows cell-by-cell so bytes do not become "b'...'"
        if isinstance(r, (tuple, list)):
            cells = []
            for v in r:
                if isinstance(v, bytes):
                    cells.append(_bytes_to_display(v, cell_max))
                else:
                    sv = "" if v is None else str(v).strip()
                    if len(sv) > cell_max:
                        sv = sv[:cell_max] + "..."
                    cells.append(sv)
            s = "(" + ", ".join(cells) + ")"
        else:
            # Non-tuple row
            if isinstance(r, bytes):
                s = _bytes_to_display(r, cell_max)
            else:
                s = str(r).strip()
                if len(s) > cell_max:
                    s = s[:cell_max] + "..."

        if s:
            out.append(s)

    final_text = "\n".join(out)

    if len(final_text) > max_chars:
        return final_text[:max_chars] + "\n... [DATA TRUNCATED] ..."

    return final_text

def regexp(expr, item):
    """
    Safe regular expression matcher for SQLite REGEXP queries.

    This function allows SQLite to apply regex matching on arbitrary column
    values without raising exceptions. It safely handles NULL values, bytes
    or BLOB data, and malformed inputs. The match is case-insensitive and
    always fails gracefully instead of crashing the query engine.

    Example:
        # SQL:
        # SELECT * FROM users WHERE email REGEXP '[a-z0-9._%+-]+@[a-z0-9.-]+';

        regexp("[a-z0-9._%+-]+@[a-z0-9.-]+", "john.doe@example.com")
        → True

        regexp("[a-z0-9._%+-]+@[a-z0-9.-]+", None)
        → False
    """
    _BIDI_CTRL_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
    
    # 1. Handle NULLs (None in Python)
    if item is None:
        return False
    
    try:
        # 2. Ensure item is a string (handles BLOBs/Bytes)
        if isinstance(item, bytes):
            item = item.decode('utf-8', errors='ignore')
        else:
            item = str(item)
            
        # Clean invisible marks + whitespace
        item = _BIDI_CTRL_RE.sub("", item)
        item = item.replace("\u00a0", " ")
        item = re.sub(r"\s+", " ", item).strip()
        
        # 3. Compile and search
        return re.search(expr, item, re.IGNORECASE) is not None
    except Exception as e:
        # Log error but don't crash SQLite
        preview = repr(item)[:200]  # avoid huge spam
        expr_preview = repr(expr)[:200]
        print(f"[REGEXP ERROR] {type(e).__name__}: {e} | expr={expr_preview} | item={preview}", file=sys.stderr)
        return False


def normalize_sql(sql: str) -> str:    
    """
    Normalize LLM-generated SQL into a clean, executable SQL string.

    Input:
        sql (str): A raw SQL string that may include Markdown code fences
                   (``` or ```sql), leading language tokens (e.g. "sql"),
                   or extra whitespace.

    Output:
        str: A cleaned SQL string with all formatting artifacts removed,
             ready to be executed directly by SQLite.

    Example:
        Input:
            ```sql
            SELECT * FROM users;
            ```

        Output:
            SELECT * FROM users;
    """
    
    if not sql:
        return sql

    sql = sql.strip()

    # Remove ```sql or ``` fences
    sql = re.sub(r"^```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
    sql = re.sub(r"```$", "", sql).strip()

    # Remove leading 'sql' token if present
    if sql.lower().startswith("sql"):
        sql = sql[3:].strip()

    return sql

def upgrade_sql_remove_limit(sql: str) -> str:
    _LIMIT_RE = re.compile(r"\s+LIMIT\s+\d+\s*;?\s*$", re.IGNORECASE)
    _LIMIT_ANYWHERE_RE = re.compile(r"\s+LIMIT\s+\d+\s*(?=($|\n|UNION|ORDER|GROUP|HAVING))", re.IGNORECASE)  
    # Remove LIMIT clauses robustly (including UNION queries)
    upgraded = re.sub(r"\bLIMIT\s+\d+\b", "", sql, flags=re.IGNORECASE)
    # Clean up extra whitespace
    upgraded = re.sub(r"\s+\n", "\n", upgraded)
    upgraded = re.sub(r"\n\s+\n", "\n", upgraded)
    upgraded = re.sub(r"\s{2,}", " ", upgraded).strip()
    return upgraded


def safe_json_loads(text: str, default):
    """
    Safely parse JSON from LLM-generated text.

    Input:
        text (str): A raw string that may contain JSON wrapped in Markdown
                    code fences (```), prefixed with a language token
                    (e.g. "json"), or include extra whitespace.
        default:    A fallback value to return if JSON parsing fails.

    Output:
        Any: The parsed Python object if valid JSON is found; otherwise
             the provided default value.

    Example:
        Input:
            ```json
            { "found": true, "confidence": 0.85 }
            ```

        Output:
            { "found": True, "confidence": 0.85 }
    """
    if not text:
        return default

    text = text.strip()

    # Remove markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()

    # Remove leading 'json' token
    if text.lower().startswith("json"):
        text = text[4:].strip()

    try:
        return json.loads(text)
    except Exception as e:
        print("[JSON PARSE ERROR]")
        print("RAW:", repr(text))
        print("ERROR:", e)
        return default


def split_union_selects(sql: str) -> list[str]:
    """
    Split a SQL query into individual SELECT statements joined by UNION or UNION ALL.

    Input:
        sql (str): A single SQL query string that may contain multiple SELECT
                   statements combined using UNION or UNION ALL.

    Output:
        list[str]: A list of individual SELECT statement strings, with UNION
                   keywords removed and whitespace normalized.

    Example:
        Input:
            SELECT email FROM users
            UNION ALL
            SELECT handle FROM accounts

        Output:
            [
                "SELECT email FROM users",
                "SELECT handle FROM accounts"
            ]
    """
    # Normalize spacing
    sql = re.sub(r"\s+", " ", sql.strip())

    # Split on UNION or UNION ALL, case-insensitive
    parts = re.split(r"\bUNION(?:\s+ALL)?\b", sql, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]

def extract_select_columns(select_sql: str) -> list[str]:
    """
    Extract column names or column aliases from a single SELECT statement.

    Input:
        select_sql (str): A SQL SELECT statement containing an explicit
                          projection list (no SELECT *), such as:
                          "SELECT col, col2 AS alias FROM table".

    Output:
        list[str]: A list of column names or aliases in the order they appear
                   in the SELECT clause.

    Example:
        Input:
            SELECT email, username AS user FROM users

        Output:
            ["email", "user"]
    """
    m = re.search(
        r"SELECT\s+(.*?)\s+FROM\s",
        select_sql,
        flags=re.IGNORECASE | re.DOTALL
    )
    if not m:
        return []

    select_list = m.group(1)

    columns = []
    for item in select_list.split(","):
        item = item.strip()

        # Handle aliases: col AS alias or col alias
        alias_match = re.search(r"\bAS\s+(\w+)$", item, re.IGNORECASE)
        if alias_match:
            columns.append(alias_match.group(1))
        else:
            # Take the final identifier
            columns.append(item.split()[-1])

    return columns


def is_sqlite_file(p: Path) -> bool:
    try:
        with p.open("rb") as f:
            return f.read(16) == b"SQLite format 3\x00"
    except Exception:
        return False

def build_db_paths(
    db_dir: Path,
    db_files: List[str],
    is_sqlite_fn,
) -> Tuple[List[Path], List[str], List[str]]:
    """
    Build ordered paths from filenames, skipping missing and non-sqlite.
    Returns (db_paths, missing, not_sqlite).
    """
    db_paths: List[Path] = []
    missing: List[str] = []
    not_sqlite: List[str] = []

    for name in db_files:
        p = db_dir / name
        if not p.exists():
            missing.append(str(p))
            continue
        if not is_sqlite_fn(p):
            not_sqlite.append(str(p))
            continue
        db_paths.append(p)

    return db_paths, missing, not_sqlite

def print_db_path_report(db_paths: List[Path], missing: List[str], not_sqlite: List[str]) -> None:
    print(f"Will process {len(db_paths)} databases (from db_files list).")
    if missing:
        print("Missing files:")
        for x in missing:
            print("  -", x)
    if not_sqlite:
        print("Not SQLite (bad header):")
        for x in not_sqlite:
            print("  -", x)

def save_jsonl(results, out_dir: Path, db_path: str) -> Path:
    """
    Save one JSONL file per database.
    Filename includes database stem + UTC timestamp.
    Converts bytes/BLOBs to JSON-safe base64.
    """
    out_dir.mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    db_stem = Path(db_path).stem
    out_path = out_dir / f"PII_{db_stem}_{ts}.jsonl"

    with out_path.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(json_safe(r), ensure_ascii=False) + "\n")

    print(f"Wrote: {out_path.resolve()}")
    return out_path


def load_config_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def load_vars_from_py(py_path: Path, *var_names: str):
    spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load module from {py_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    out = {}
    for name in var_names:
        if not hasattr(mod, name):
            raise AttributeError(f"{py_path} does not define `{name}`")
        out[name] = getattr(mod, name)
    return out

import base64

# sanitize each result dict before writing JSONL
def json_safe(obj):
    if isinstance(obj, bytes):
        # base64 keeps it compact and reversible
        return {"__bytes_b64__": base64.b64encode(obj).decode("ascii")}
        # or use hex:
        # return {"__bytes_hex__": obj.hex()}
    if isinstance(obj, tuple):
        return [json_safe(x) for x in obj]
    if isinstance(obj, list):
        return [json_safe(x) for x in obj]
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    return obj
