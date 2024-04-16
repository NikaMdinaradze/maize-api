build:
	@echo "building API development server docker"
	docker-compose build

run:
	@echo "starting API development server docker"
	docker-compose up

get_requirements:
	@echo "getting requirements"
	docker-compose run --rm web pip list

init_aerich:
	@echo "initializing config file and location"
	docker-compose run --rm web aerich init -t src.settings.TORTOISE_CONFIG

init_db:
	@echo "initializing database"
	docker-compose run --rm web aerich init -t src.settings.TORTOISE_CONFIG

migrate:
	@echo "making migrations"
	docker-compose run --rm web aerich migrate --name $(name)

upgrade:
	@echo "upgrading database"
	docker-compose run --rm web aerich upgrade
