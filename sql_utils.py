import re
import json


def rows_to_text(rows, limit=None, max_chars=500000, cell_max=500):
    """
    Converts SQL rows to text with safety limits for LLM context.
    - limit: Max number of rows to process.
    - max_chars: Hard limit for the total string length.
    - cell_max: Max length for any single column value.
    """
    if not rows:
        return ""
    
    out = []
    # 1. Row-level limiting
    target_rows = rows[:limit] if limit else rows
    
    for r in target_rows:
        print(f"Test [ROW DATA] {r}")
        if r is None:
            continue
        s = str(r).strip()  # trim whitespace first
        if len(s) == 0:
            continue
        if len(s) > cell_max:
            s = s[:cell_max] + "..."
        out.append(s)
    
    final_text = "\n".join(out)
    
    # 2. Final global character limit safety check
    if len(final_text) > max_chars:
        return final_text[:max_chars] + "\n... [DATA TRUNCATED] ..."
    
    # print(f"[ROWS TO TEXT] Input: {len(rows)} rows | Output: {len(final_text)} chars")
    # Optional: print only the first 200 characters of the text to keep logs clean
    # print(f"[PREVIEW]: {final_text[:200]}...")
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
    # 1. Handle NULLs (None in Python)
    if item is None:
        return False
    
    try:
        # 2. Ensure item is a string (handles BLOBs/Bytes)
        if isinstance(item, bytes):
            item = item.decode('utf-8', errors='ignore')
        else:
            item = str(item)
            
        # 3. Compile and search
        return re.search(expr, item, re.IGNORECASE) is not None
    except Exception:
        # 4. If anything else goes wrong, don't crash SQLite
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