"""Draws schema.png from the tables and foreign keys in the database.

Only this script needs matplotlib:  pip install matplotlib
"""
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import db

WIDTH = 3.0       # table box width
HEADER = 0.5      # table name bar height
ROW = 0.4         # height of one column row

# top-left corner of each table box
POSITIONS = {
    "conductor": (0.0, 10.0),
    "ensemble": (4.6, 10.0),
    "membership": (9.2, 10.0),
    "section": (13.8, 10.0),
    "parent": (0.0, 5.2),
    "player_parent": (4.6, 5.2),
    "player": (9.2, 5.2),
}

HEADER_COLOR = "#2f4b7c"
LINE_COLOR = "#555555"


def load_tables():
    """{table: {"columns": [(name, type, is_pk)], "fks": {column: (ref_table, ref_column)}}}"""
    con = sqlite3.connect(db.DB_PATH)
    tables = {}
    for table in POSITIONS:
        columns = [(row[1], row[2], row[5] > 0) for row in con.execute(f"pragma table_info({table})")]
        fks = {row[3]: (row[2], row[4]) for row in con.execute(f"pragma foreign_key_list({table})")}
        tables[table] = {"columns": columns, "fks": fks}
    con.close()
    return tables


def row_y(table, column, tables):
    """Vertical centre of a column's row."""
    names = [c[0] for c in tables[table]["columns"]]
    top = POSITIONS[table][1]
    return top - HEADER - (names.index(column) + 0.5) * ROW


def draw_table(ax, table, info):
    x, top = POSITIONS[table]
    height = HEADER + ROW * len(info["columns"])
    ax.add_patch(Rectangle((x, top - height), WIDTH, height, facecolor="white", edgecolor=HEADER_COLOR, linewidth=1.5, zorder=2))
    ax.add_patch(Rectangle((x, top - HEADER), WIDTH, HEADER, facecolor=HEADER_COLOR, edgecolor=HEADER_COLOR, zorder=3))
    ax.text(x + WIDTH / 2, top - HEADER / 2, table, color="white", fontsize=12, fontweight="bold", ha="center", va="center", zorder=4)

    for i, (name, col_type, is_pk) in enumerate(info["columns"]):
        y = top - HEADER - (i + 0.5) * ROW
        keys = " ".join(k for k, on in (("PK", is_pk), ("FK", name in info["fks"])) if on)
        ax.text(x + 0.1, y, keys, fontsize=7, color="#b5651d", fontweight="bold", va="center", zorder=4)
        ax.text(x + 0.62, y, name, fontsize=9.5, fontweight="bold" if is_pk else "normal", va="center", zorder=4)
        ax.text(x + WIDTH - 0.1, y, col_type, fontsize=7.5, color="#777777", ha="right", va="center", zorder=4)


def draw_relationship(ax, table, column, ref_table, ref_column, tables):
    """Elbow line from the foreign key row (many) to the primary key row it references (one)."""
    x, top = POSITIONS[table]
    ref_x, ref_top = POSITIONS[ref_table]
    y = row_y(table, column, tables)
    ref_y = row_y(ref_table, ref_column, tables)

    if top == ref_top:                       # side by side
        if ref_x < x:
            start, end = x, ref_x + WIDTH
        else:
            start, end = x + WIDTH, ref_x
        bend = (start + end) / 2
    else:                                    # stacked: loop out to the left
        start, end = x, ref_x
        bend = x - 0.4

    ax.plot([start, bend, bend, end], [y, y, ref_y, ref_y], color=LINE_COLOR, linewidth=1.3, zorder=1)
    toward = 1 if bend > start else -1
    ax.text(start + 0.12 * toward, y + 0.1, "N", fontsize=8, color=LINE_COLOR, ha="center")
    toward = 1 if bend > end else -1
    ax.text(end + 0.12 * toward, ref_y + 0.1, "1", fontsize=8, color=LINE_COLOR, ha="center")


def main():
    db.build_db()
    tables = load_tables()

    fig, ax = plt.subplots(figsize=(16, 8))
    for table, info in tables.items():
        draw_table(ax, table, info)
        for column, (ref_table, ref_column) in info["fks"].items():
            draw_relationship(ax, table, column, ref_table, ref_column, tables)

    ax.set_title("Youth Orchestra Database Schema", fontsize=16, fontweight="bold", pad=12)
    ax.text(8.4, 1.75, "PK = primary key    FK = foreign key    N / 1 = many-to-one", fontsize=9, color=LINE_COLOR, ha="center")
    ax.set_xlim(-0.5, 17.3)
    ax.set_ylim(1.5, 10.4)
    ax.set_aspect("equal")
    ax.axis("off")

    out_path = db.get_path("schema.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
