.PHONY: prepare_env start stop restart logs test


prepare_env:
	@./prepare_config_files.sh
	@docker compose build --no-cache

start:
	docker compose up -d

stop:
	docker compose stop

restart: stop start

logs:
	@docker compose logs --tail 60 -f user_manager

test:
	@docker compose run --rm user_manager ./run_tests -s
