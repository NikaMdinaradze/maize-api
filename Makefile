build:
	@echo "building API development server docker"
	docker-compose build

run:
	@echo "starting API development server docker"
	docker-compose up

get_requirements:
	@echo "getting requirements"
	docker-compose run --rm web pip list
