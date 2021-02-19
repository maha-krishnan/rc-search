# install all the python package from requirements.txt in editable mode
deps:
	pip install --upgrade pip
	pip install -r requirements.txt  --index-url https://admin:AP4crtTCxHc32R7zM5D9qmsZbwGhHWh9iRfaZ7@rightart.jfrog.io/artifactory/api/pypi/pypi/simple
	pip install --editable .
	( \
       . .env/bin/activate; \
    )

# create python3 virtual environment .env
dev-env:
	python3 -m venv .env

# execute consumer.py file in port 5628 to validate the files
run:
	python consumer.py worker -l info -p 5628

# start the rc_search service
start:
	rc_search start-server

# start the docker container in background
infra-up:
	docker-compose up -d

# stops the conatiner and removes volumes, images created by UP command.
infra-down:
	docker-compose down

# run all the test cases.
test:
	python -m unittest discover tests "*_test.py"
	pytest

# create the test report by running all the test case
test-reports:
	pytest --junitxml=pytest-report.xml
	coverage run --source lib -m unittest discover tests "*_test.py" || true
	coverage xml --skip-empty -i -o ./reports/coverage.xml

# get the code coverage of the project
coverage:
	coverage erase
	coverage run --source lib -m unittest discover tests "*_test.py" | true
	coverage report -m

docker-test:
	docker-compose -p rc-search -f ./docker-compose-test.yml build --no-cache
	docker-compose -p rc-search -f ./docker-compose-test.yml up -d
	sleep 5
	docker ps
	docker exec  -t rc-search_rc-search_1 make test-reports || true
	docker cp rc-search_rc-search_1:/install/reports ./reports/ || true
	docker-compose -p rc-search_rc-search_1 -f ./docker-compose-test.yml down || true	

sonar:
	pytest --junitxml=pytest-report.xml | true
	coverage erase
	coverage run -m unittest discover tests "*_test.py" | true
	coverage xml -i
	sonar-scanner \
		-Dsonar.projectKey=rc-search \
		-Dsonar.sources=. \
		-Dsonar.host.url=http://localhost:9000 \
		-Dsonar.login=70ed844569842b5405e81c1489e96ab1805c258d

# to avoid name conflict with target
.PHONY: deps test sonar coverage coverage-report