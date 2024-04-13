deps:
	uv pip compile pyproject.toml -o requirements.txt

dev-deps: deps
	uv pip compile --extra=dev pyproject.toml -o dev_requirements.txt

install-dev-deps: dev-deps
	uv pip sync requirements.txt dev_requirements.txt

install-deps: deps
	uv pip sync requirements.txt

lint:
	ruff check --fix --unsafe-fixes --target-version py311 app
	pyright app

format:
	ruff format --target-version py311 app

dev:
	uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

test:
	pytest --disable-warnings

run_prod:
	alembic upgrade head
	uvicorn app.main:app --port 8000 --host 0.0.0.0
