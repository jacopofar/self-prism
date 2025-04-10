import logging
from typing import Annotated

from litestar import get, post, delete
from litestar.response import Template
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK

from src.search import Search
from src.db import db
from src.visits import Visit, VisitRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@post("/log_visit")
async def log_visit(data: VisitRequest) -> int:
    visit = Visit.from_visit_request(data)
    logger.info(f"Visit at {visit.url}")
    db.insert_visit(visit)
    return visit.id


@get("/archive/{item_id:int}", name="archive")
async def get_visit(item_id: int) -> Template:
    visit = db.get_visit(item_id)
    return Template(template_name="archive.html.jinja2", context={"visit": visit})


@delete("/delete/{item_id:int}", name="delete", status_code=HTTP_200_OK)
async def delete_visit(item_id: int) -> None:
    db.delete_visit(item_id)


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
