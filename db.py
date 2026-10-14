"""Builds the SQLite database from the .sql files and runs read-only queries on it."""
import os
import sqlite3
from pathlib import Path

fdir = os.path.dirname(os.path.abspath(__file__))


def get_path(fname):
    return os.path.join(fdir, fname)


DB_PATH = get_path("aidb.sqlite")
SETUP_SQL_PATH = get_path("setup.sql")
SETUP_DATA_PATH = get_path("setupData.sql")


def read_schema():
    """The CREATE TABLE statements, exactly as they are sent to GPT."""
    with open(SETUP_SQL_PATH) as f:
        return f.read().strip()


def build_db():
    """Erase any previous database and rebuild it from setup.sql and setupData.sql."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with open(SETUP_DATA_PATH) as f:
        data_script = f.read()

    con = sqlite3.connect(DB_PATH)
    con.executescript(read_schema())  # tables and keys
    con.executescript(data_script)    # mock data
    con.commit()
    con.close()


def _connect_read_only():
    # mode=ro makes SQLite itself refuse any write, whatever SQL GPT hands us
    return sqlite3.connect(Path(DB_PATH).as_uri() + "?mode=ro", uri=True)


def run_sql(query):
    """Run one SELECT statement. Returns (column_names, rows)."""
    query = query.strip().rstrip(";").strip()
    first_word = query.split(None, 1)[0].lower() if query else ""
    if first_word not in ("select", "with"):
        raise ValueError("Only SELECT statements are allowed.")

    con = _connect_read_only()
    try:
        cursor = con.execute(query)  # execute() rejects multiple statements
        columns = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
    finally:
        con.close()
    return columns, rows


def table_names():
    _, rows = run_sql(
        "select name from sqlite_master where type = 'table' and name not like 'sqlite_%' order by rowid"
    )
    return [row[0] for row in rows]


def sample_rows(limit=3):
    """A few rows from every table, as text, so GPT can see what the data looks like."""
    parts = []
    for table in table_names():
        columns, rows = run_sql(f"select * from {table} limit {limit}")
        lines = [f"/* {limit} example rows from {table}:", " | ".join(columns)]
        lines += [" | ".join(str(value) for value in row) for row in rows]
        parts.append("\n".join(lines) + " */")
    return "\n\n".join(parts)


if __name__ == "__main__":
    build_db()
    print(f"Built {DB_PATH}")
    for table in table_names():
        _, rows = run_sql(f"select count(*) from {table}")
        print(f"  {table}: {rows[0][0]} rows")
