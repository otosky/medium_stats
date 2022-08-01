fmt:
	poetry run isort . && \
	poetry run black --exclude .venv .

test:
	poetry run pytest

cov:
	poetry run pytest --cov=. --cov-branch -v --durations=25
	poetry run coverage report -m
	poetry run coverage html
	open htmlcov/index.html
