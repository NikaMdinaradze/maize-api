.PHONY: migrations
.PHONY: tests

build:
	@echo "Building development server docker"
	docker-compose build

run:
	@echo "starting API development server docker"
	docker-compose up

get_requirements:
	@echo "getting requirements"
	docker-compose run --rm web pip list

migrations:
	@echo "making migrations"
	docker-compose run --rm web alembic revision --autogenerate -m "$(name)"

migrate:
	@echo "migrating"
	docker-compose run --rm web alembic upgrade head

test:
	@echo "running tests..."
	docker-compose -f docker-compose.test.yml run --rm web sh -c "pytest"
