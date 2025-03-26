import os
from pathlib import Path
from litestar import Litestar
from litestar.config.cors import CORSConfig

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
    ],
    cors_config=cors_config,
)
