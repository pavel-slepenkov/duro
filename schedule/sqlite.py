import sqlite3
from typing import List, Tuple

import arrow
import networkx as nx


def save_to_db(graph: nx.DiGraph, db_path: str, commit: str):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    nodes = dict(graph.nodes(data=True))
    tables_and_queries = [(k, v['contents'], v['interval']) for k, v in
                          nodes.items()]
    save_tables(tables_and_queries, cursor)
    save_commit(commit, cursor)
    mark_deleted_tables(tables_and_queries, cursor)

    connection.commit()
    connection.close()


def save_tables(tables_and_queries: List[Tuple], cursor):
    try:
        for table, query, interval in tables_and_queries:
            cursor.execute('''UPDATE tables 
                            SET query = ?, interval = ?
                            WHERE table_name = ? ''', (query, interval, table))
            if cursor.rowcount == 0:
                cursor.execute('''INSERT INTO tables 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (table, query,
                                interval, None,
                                0, 0,
                                1,
                                0, None))
    except sqlite3.OperationalError as e:
        if str(e).startswith('no such table'):
            cursor.execute('''CREATE TABLE IF NOT EXISTS tables
                                (table_name text, query text, 
                                interval integer, last_created integer,
                                mean real, times_run integer,
                                force integer, 
                                started integer, deleted integer);''')
            save_tables(tables_and_queries, cursor)
        else:
            raise


def save_commit(commit: str, cursor):
    if commit is not None:
        try:
            cursor.execute('''INSERT INTO commits VALUES (?, ?)''',
                           (commit, arrow.now().timestamp))
        except sqlite3.OperationalError as e:
            if str(e).startswith('no such table'):
                cursor.execute('''CREATE TABLE IF NOT EXISTS commits
                                            (hash text, processed integer)''')
                save_commit(commit, cursor)
            else:
                raise


def mark_deleted_tables(tables_and_queries: List[Tuple], cursor):
    tables = tuple(table for table, _, _ in tables_and_queries)
    cursor.execute(f'''UPDATE tables
                    SET deleted = strftime('%s', 'now')
                    WHERE table_name NOT IN {str(tables)}
                    AND deleted IS NULL''')
