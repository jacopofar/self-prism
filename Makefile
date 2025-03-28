bootstrap:
	cp .env.template .env

migrate:
	uv run --env-file .env scripts/migrate.py

run: migrate
	uv run --env-file .env litestar --app src.app:app run --port 8987

run_dev: migrate
	uv run --env-file .env litestar --app src.app:app run --debug --reload-dir src --port 8987

format:
	uv run --env-file .env ruff format src scripts

test:
	uv run pytest -s
