install:
	pip3 install -r requirements.txt

db/run:
	docker-compose up -d --force-recreate
	make db/wait
	make db/create

db/create:
	echo "creating tables"; \
	until docker exec -i "$(shell docker-compose ps -q)" sh -c "PGPASSWORD=admin psql -h localhost -U admin -d postgres a -f /docker-entrypoint-initdb.d/data_base.sql > /dev/null 2>&1"; do \
	printf "."; sleep 1s; \
	done; \
	echo "created";

db/clean:
	docker-compose stop && docker-compose rm -vf

db/wait:
	echo "waiting postgres"; \
	until docker exec -i "$(shell docker-compose ps -q)" sh -c "PGPASSWORD=admin psql -h localhost -U admin -d postgres -c 'select 1' > /dev/null 2>&1"; do \
	printf "."; sleep 1s; \
	done; \
	echo "postgres is up";

DB_USER ?= admin
DB_PASSWORD ?= admin
DB_HOST ?= localhost
DB_PORT ?= 5433
DB_NAME ?= postgres
DB_URL := postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)