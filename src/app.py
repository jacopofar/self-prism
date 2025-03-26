import os
from pathlib import Path
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
import src.handlers as handlers

cors_config = CORSConfig(
    allow_origins=["*"],
    allow_credentials=True,
    expose_headers=["*"],
    allow_headers=["*"],
)


app = Litestar(
    [
        handlers.log_visit,
        handlers.get_visit,
        handlers.get_search,
    ],
    cors_config=cors_config,
    template_config=TemplateConfig(
        directory=os.path.dirname(__file__) / Path("templates"),
        engine=JinjaTemplateEngine,
    ),
)
