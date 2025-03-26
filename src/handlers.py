from litestar import post
from src.db import db
from src.visits import Visit, VisitRequest


@post("/log_visit")
async def log_visit(data: VisitRequest) -> int:
    visit = Visit.from_visit_request(data)
    db.insert_visit(visit)
    return visit.id
