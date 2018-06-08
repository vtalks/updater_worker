VERSION=`cat VERSION`

# Test

.PHONY: test
test:	## Execute tests suites
	python3 -m unittest discover -v


.PHONY: cover
cover:	## Generate coverage information
	coverage3 run --omit=*.venv*,main.py --source=. -m unittest discover

.PHONY: coverage-html
coverage-html:	cover ## HTML report
	coverage3 html --directory=.cover --omit=*.venv*,main.py

.PHONY: coveralls
coveralls:	## Coverage to coveralls report
	coveralls --data_file=.coverage --coveralls_yaml=.coveralls.yml --base_dir=.


# Docker container images

.PHONY: docker
docker: docker-build docker-publish

.PHONY: docker-build
docker-build:	## Builds container and tag resulting image
	docker build --force-rm --tag vtalks/updater-worker .
	docker tag vtalks/updater-worker vtalks/updater-worker:$(VERSION)

.PHONY: docker-publish
docker-publish:	## Publishes container images
	docker push vtalks/updater-worker:$(VERSION)
	docker push vtalks/updater-worker:latest

include Makefile.help.mk