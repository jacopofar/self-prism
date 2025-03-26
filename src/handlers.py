from typing import Annotated
from litestar import get, post
from litestar.response import Template
from litestar.params import Parameter


from src.search import Search
from src.db import db
from src.visits import Visit, VisitRequest


@post("/log_visit")
async def log_visit(data: VisitRequest) -> int:
    visit = Visit.from_visit_request(data)
    db.insert_visit(visit)
    return visit.id


@get("/archive/{item_id:int}", name="archive")
async def get_visit(item_id: int) -> Template:
    visit = db.get_visit(item_id)
    return Template(template_name="archive.html.jinja2", context={"visit": visit})


@get(["/search", "/"])
async def get_search(
    search_term: Annotated[str | None, Parameter(query="query")],
) -> Template:
    if search_term is None or search_term.strip() == "":
        visits = db.latest_visits()
    else:
        visits = Search.semantic_search(search_term)
    return Template(
        template_name="search.html.jinja2",
        context={"query": search_term, "visits": visits},
    )
