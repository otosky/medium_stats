fmt:
	poetry run isort . && \
	poetry run black --exclude .venv .

test:
	poetry run pytest