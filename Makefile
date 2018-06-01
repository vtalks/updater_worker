VERSION=`cat VERSION`

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