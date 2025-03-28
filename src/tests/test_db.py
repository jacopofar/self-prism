from unittest.mock import patch
import pytest

from src.db import DB
from src.visits import Visit


@pytest.fixture(autouse=True)
def mock_embeddings():
    class FakeEmbeddings:
        def __init__(self) -> None:
            pass

        def encode(self, sentences):
            return [0.1] * 384

    with (
        patch("src.embeddings.Embeddings", FakeEmbeddings),
        patch("src.embeddings.embeddings", FakeEmbeddings()),
    ):
        yield


@pytest.fixture()
def db():
    d = DB(":memory:")
    d.migrate()

    yield d


class TestDb:
    def test_db_insert_visit(self, db: DB):
        visit = Visit(
            url="example.com",
            title="Example",
            description="Example description",
            referrer="",
            content_html="Hello world",
        )
        visit_id = db.insert_visit(visit)

        assert visit_id is not None

        db_visit = db.get_visit(visit_id)

        assert visit.url == db_visit.url
        assert visit.title == db_visit.title
        assert visit.description == db_visit.description
        assert visit.referrer == db_visit.referrer
        assert visit.content_html == db_visit.content_html

        assert db.con.execute("SELECT COUNT(*) FROM visits").fetchone() == (1,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_html").fetchone() == (1,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_embeddings").fetchone() == (
            1,
        )

    def test_db_upsert_visit(self, db: DB):
        visit = Visit(
            url="example.com",
            title="Example",
            description="Example description",
            referrer="",
            content_html="Hello world",
        )
        visit_id = db.insert_visit(visit)

        upserted_visit = Visit(
            url="example.com",
            title="Example",
            description="Example description",
            referrer="",
            content_html="Hello world. Something new happened",
        )
        upserted_visit_id = db.insert_visit(upserted_visit)

        assert upserted_visit_id is not None
        assert visit_id == upserted_visit_id

        db_visit = db.get_visit(upserted_visit_id)

        assert upserted_visit.url == db_visit.url
        assert upserted_visit.title == db_visit.title
        assert upserted_visit.description == db_visit.description
        assert upserted_visit.referrer == db_visit.referrer
        assert upserted_visit.content_html == db_visit.content_html

        assert db.con.execute("SELECT COUNT(*) FROM visits").fetchone() == (1,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_html").fetchone() == (1,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_embeddings").fetchone() == (
            1,
        )

    def test_db_delete_visit(self, db: DB):
        visit = Visit(
            url="example.com",
            title="Example",
            description="Example description",
            referrer="",
            content_html="Hello world",
        )
        visit_id = db.insert_visit(visit)

        assert visit_id is not None

        db_visit = db.get_visit(visit_id)

        assert db_visit.id == visit_id

        assert db.con.execute("SELECT COUNT(*) FROM visits").fetchone() == (1,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_html").fetchone() == (1,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_embeddings").fetchone() == (
            1,
        )

        db.delete_visit(visit_id)

        assert db.con.execute("SELECT COUNT(*) FROM visits").fetchone() == (0,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_html").fetchone() == (0,)
        assert db.con.execute("SELECT COUNT(*) FROM visits_embeddings").fetchone() == (
            0,
        )
