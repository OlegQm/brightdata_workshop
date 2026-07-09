DC = docker compose
DC_DL = docker compose -f docker-compose.data-download.yml

download-boundary:
	$(DC_DL) --profile download-0 run --rm generate-czsk-boundary

download-tiles:
	$(DC_DL) --profile download-0 run --rm --build download-sk-cz-tiles

download-photon:
	$(DC_DL) --profile download-0 run --rm --build download-photon-pbf

download-0: download-boundary download-tiles download-photon

up:
	$(DC) up

up-build:
	$(DC) up --build

download-and-up: download-0 up-build

down:
	$(DC) down

.PHONY: download-boundary download-tiles download-photon download-0 up up-build download-and-up down
