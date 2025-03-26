import logging
import sqlite3
import sqlite_zstd
import sqlite_vec

from src.visits import Visit


class DB:
    def __init__(self, path: str):
        self.con = sqlite3.connect(path)

        self.con.execute("PRAGMA journal_mode = WAL")
        self.con.execute("PRAGMA synchronous = NORMAL")
        self.con.execute("PRAGMA auto_vacuum = full")
        self.con.execute("PRAGMA foreign_keys = ON")

        # load extensions
        self.con.enable_load_extension(True)
        sqlite_zstd.load(self.con)
        sqlite_vec.load(self.con)
        self.con.enable_load_extension(False)

    def migrate(self):
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                description TEXT,
                referrer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at_week TEXT GENERATED ALWAYS AS (strftime('%Y-%W', created_at)) VIRTUAL
            )
            """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS visits_url_created_at_week_idx ON visits(url, created_at_week)
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS visits_html (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visit_id INTEGER NOT NULL,
                content_html TEXT,
                FOREIGN KEY (visit_id) REFERENCES visits (id) ON DELETE CASCADE
            )
            """)
        try:
            cur.execute(
                """SELECT zstd_enable_transparent('{"table": "visits_html", "column": "content_html", "compression_level": 19, "dict_chooser": "''a''"}')"""
            )
        except sqlite3.OperationalError:
            # cannot enable if already enabled
            pass
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS visits_embeddings USING vec0(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visit_id INTEGER NOT NULL,
                embeddings float[384]
                -- vec0 doesn't support foreign keys at this stage
                -- FOREIGN KEY (visit_id) REFERENCES visits (id)
            )
            """)
        self.con.commit()

    def insert_visit(self, visit: Visit) -> int | None:
        # Start a transaction
        self.con.execute("BEGIN TRANSACTION")
        cur = self.con.cursor()
        row = cur.execute(
            "SELECT id FROM visits WHERE url = ? AND created_at_week = strftime('%Y-%W', 'now')",
            [visit.url],
        ).fetchone()
        if row is None:
            return self.__insert_visit(cur, visit)
        else:
            visit.id = row[0]
            return self.__update_visit(cur, visit)

    def __insert_visit(self, cur: sqlite3.Cursor, visit: Visit) -> int | None:
        try:
            cur.execute(
                """
                INSERT INTO visits (url, title, description, referrer)
                VALUES (?, ?, ?, ?)
                """,
                (
                    visit.url,
                    visit.title,
                    visit.description,
                    visit.referrer,
                ),
            )
            visit_id = cur.lastrowid

            cur.execute(
                """
                INSERT INTO visits_html (visit_id, content_html)
                VALUES (?, ?)
                """,
                (visit_id, visit.content_html),
            )

            cur.execute(
                """
                INSERT INTO visits_embeddings (visit_id, embeddings)
                VALUES (?, ?)
                """,
                (
                    visit_id,
                    sqlite_vec.serialize_float32(visit.embeddings),
                ),
            )

            # Commit the transaction
            self.con.commit()

            return visit_id

        except sqlite3.Error:
            logging.exception("failed to insert visit")
            self.con.rollback()
            return None

    def __update_visit(self, cur: sqlite3.Cursor, visit: Visit) -> int | None:
        try:
            cur.execute(
                """
                UPDATE visits SET title = ?, description = ?, referrer = ?
                WHERE id = ?
                """,
                (
                    visit.title,
                    visit.description,
                    visit.referrer,
                    visit.id,
                ),
            )

            cur.execute(
                """
                UPDATE visits_html SET content_html = ?
                WHERE visit_id = ?
                """,
                (visit.content_html, visit.id),
            )

            cur.execute(
                """
                UPDATE visits_embeddings SET embeddings = ?
                WHERE visit_id = ?
                """,
                (
                    sqlite_vec.serialize_float32(visit.embeddings),
                    visit.id,
                ),
            )

            # Commit the transaction
            self.con.commit()

            return visit.id

        except sqlite3.Error:
            logging.exception("failed to insert visit")
            self.con.rollback()
            return None

    def semantic_search(self, embeddings: list[float], limit=20):
        cur = self.con.cursor()
        rows = cur.execute(
            """
            WITH search_subquery AS (
                SELECT ve.visit_id AS visit_id FROM visits_embeddings ve
                WHERE ve.embeddings MATCH ?
                ORDER BY ve.distance
                LIMIT ?
            )
            SELECT ss.visit_id, v.url, v.title, v.description, v.referrer FROM search_subquery ss
            JOIN visits v ON ss.visit_id = v.id
        """,
            [sqlite_vec.serialize_float32(embeddings), limit],
        ).fetchall()
        return [
            Visit(
                id=row[0],
                url=row[1],
                title=row[2],
                description=row[3],
                referrer=row[4],
                content_html="",
            )
            for row in rows
        ]

    def latest_visits(self, limit=20):
        cur = self.con.cursor()
        rows = cur.execute(
            """
            SELECT
                v.id,
                v.url,
                v.title,
                v.description,
                v.referrer
            FROM visits v
            ORDER BY id DESC
            LIMIT ?
        """,
            [limit],
        ).fetchall()
        return [
            Visit(
                id=row[0],
                url=row[1],
                title=row[2],
                description=row[3],
                referrer=row[4],
                content_html="",
            )
            for row in rows
        ]

    def get_visit(self, item_id: int):
        cur = self.con.cursor()
        row = cur.execute(
            """
            SELECT
                v.id,
                v.url,
                v.title,
                v.description,
                v.referrer,
                vh.content_html
            FROM visits v
            JOIN visits_html vh ON vh.visit_id = v.id
            WHERE v.id = ?
            """,
            (item_id,),
        ).fetchone()

        return Visit(
            id=row[0],
            url=row[1],
            title=row[2],
            description=row[3],
            referrer=row[4],
            content_html=row[5],
        )

    def delete_visit(self, item_id: int):
        self.con.execute("BEGIN TRANSACTION")
        cur = self.con.cursor()
        cur.execute(
            """
            DELETE FROM visits WHERE id = ?
            """,
            (item_id,),
        )
        cur.execute(
            """
            DELETE FROM visits_embeddings WHERE visit_id = ?
            """,
            (item_id,),
        )
        self.con.commit()


db = DB("prism.sqlite3")
