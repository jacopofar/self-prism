from dataclasses import dataclass
from functools import cached_property
import io
from markitdown import MarkItDown


from src.embeddings import embeddings


@dataclass
class VisitRequest:
    url: str
    title: str
    description: str | None
    referrer: str
    content_html: str


mark = MarkItDown()


@dataclass
class Visit:
    url: str
    title: str
    description: str | None
    referrer: str
    content_html: str

    id: int | None = None
    """id is None when not inserted in database"""

    @staticmethod
    def from_visit_request(req: VisitRequest):
        return Visit(
            url=req.url,
            title=req.title,
            description=req.description,
            referrer=req.referrer,
            content_html=req.content_html,
        )

    @cached_property
    def markdown(self):
        return mark.convert_stream(io.BytesIO(self.content_html.encode())).markdown

    @cached_property
    def embeddings(self):
        return embeddings.encode(self.markdown)
