from sqlite3 import Row
from typing import Dict, Tuple

from networkx import DiGraph

from utils.global_config import load_global_config
from utils.graph_utils import get_all_successors


def get_all_tables(db):
    return db.execute(
        """
        SELECT table_name, interval, last_created, 
            mean, started, deleted, force
        FROM tables
        WHERE (strftime('%s', 'now') - deleted) / (3600 * 24) < 7
            OR deleted is null
        ORDER BY last_created DESC
        """
    ).fetchall()


def get_jobs(floor: int, ceiling: int, db) -> Tuple[Row]:
    return db.execute(
        """
        SELECT "table", 
            "start",
            COALESCE(drop_old, "insert") AS "finish"
        FROM timestamps
        WHERE "start" BETWEEN ? AND ?
        
        UNION ALL
        
        SELECT table_name AS "table",
            started AS "start",
            NULL AS "finish"
        FROM tables
        WHERE started IS NOT NULL
        AND deleted IS NULL
        
    """,
        (floor, ceiling),
    ).fetchall()


def get_table_details(db, table: str, limit: int = 100):
    return db.execute(
        """
        SELECT t.table_name, t.interval,
            ts.start, ts.connect, ts."select", ts.create_temp,
            ts.process, ts.csv, ts.s3, ts."insert", ts.clean_csv,
            ts.tests, ts.replace_old, ts.drop_old, ts.make_snapshot, 
            ts.finish
        FROM tables t
        LEFT JOIN timestamps ts ON t.table_name = ts."table"
        WHERE t.table_name = ?
        ORDER BY ts.finish DESC
        LIMIT ?
    """,
        (table, limit),
    ).fetchall()


def set_table_for_update(
    db_connection, table: str, force_tree: int, config_path="config.conf"
):
    if force_tree:
        propagate_force_flag(
            db_connection, table, load_global_config(config_path).graph
        )
    else:
        db_connection.execute(
            """
            UPDATE tables
            SET force = 1
            WHERE table_name = ? 
        """,
            (table,),
        )
        db_connection.commit()


def propagate_force_flag(db_connection, table: str, graph: DiGraph):
    try:
        successors = get_all_successors(graph, table)
    except KeyError:
        return

    if not successors:
        return

    if len(successors) == 1:
        db_connection.execute(
            f"""
            UPDATE tables SET force = 1
            WHERE table_name = '{successors[0]}'
        """
        )
    else:
        db_connection.execute(
            f"""
            UPDATE tables SET force = 1
            WHERE table_name in {str(tuple(successors))}"""
        )

        db_connection.commit()


def get_overview_stats(db_connection, hours: int) -> Dict:
    cursor = db_connection.cursor()
    cursor.execute(
        """
        SELECT COUNT(DISTINCT "table"), 
            COUNT(*),
            ROUND(100.0 * SUM(finish - start) / (? * 3600), 2) 
        FROM timestamps
        WHERE (strftime('%s', 'now') - finish) / 3600 < ?
    """,
        (hours, hours),
    )

    row = cursor.fetchone()

    return {"tables": row[0], "updates": row[1], "load": row[2]}
