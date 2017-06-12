
def get_all_tables(db):
    return db.execute('''
            SELECT table_name, interval, last_created, mean
            FROM tables 
            ORDER BY last_created DESC''').fetchall()


def get_jobs(floor, ceiling, db):
    print(floor, ceiling)
    return db.execute('''
                    SELECT "table", "start", drop_old as "finish"
                    FROM timestamps
                    WHERE "start" BETWEEN ? and ?
                    ORDER BY start DESC''', (floor, ceiling)).fetchall()


def get_table_details(db, table: str):
    return db.execute('''
                SELECT t.table_name, t.interval,
                    ts.start, ts.connect, ts."select", ts.create_temp,
                    ts.process, ts.csv, ts.s3, ts."insert", ts.clean_csv,
                    ts.tests, ts.replace_old, ts.drop_old, ts.finish
                FROM tables t
                LEFT JOIN timestamps ts ON t.table_name = ts."table"
                WHERE t.table_name = ?
                ORDER BY ts.drop_old DESC''',
                      (table,)).fetchall()