.PHONY: env
env:
	@pipenv sync --dev

.PHONY: migrate
migrate:
	@pipenv run webcheckctl db migrate up

.PHONY: cleandb
cleandb:
	@pipenv run webcheckctl db migrate down

.PHONY: lint
lint:
	@pipenv run flake8

.PHONY: test
test:
	@pipenv run pytest

.PHONY: docker-image
docker-image:
	@docker build . -t webcheck

.PHONY: fixtures
fixtures:
	@pipenv run ./fixtures.sh

.PHONY: scheduler
scheduler:
	@pipenv run webcheckctl monitoring scheduler

.PHONY: checks_worker
checks_worker:
	@pipenv run webcheckctl monitoring checks_worker

.PHONY: results_worker
results_worker:
	@pipenv run webcheckctl monitoring results_worker

.PHONY: websites-list
websites-list:
	@pipenv run webcheckctl websites list

.PHONY: checks-list
checks-list:
	@pipenv run webcheckctl checks list

.PHONY: results-list
results-list:
	@pipenv run webcheckctl results list
