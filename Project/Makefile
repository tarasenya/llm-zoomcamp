.PHONY: start_elastic_search ingest_data start_basic_cli

start_elastic_search:
	docker run -it \
	--rm \
	--name elasticsearch \
	-p 9200:9200 \
	-p 9300:9300 \
	-m 3GB \
	-e "discovery.type=single-node" \
	-e "xpack.security.enabled=false" \
	docker.elastic.co/elasticsearch/elasticsearch:8.4.3

start_elastic_search_detached:
	docker run -d -it \
	--rm \
	--name elasticsearch \
	-p 9200:9200 \
	-p 9300:9300 \
	-m 3GB \
	-e "discovery.type=single-node" \
	-e "xpack.security.enabled=false" \
	docker.elastic.co/elasticsearch/elasticsearch:8.4.3

ingest_data:
	pipenv run python src/data_ingestion.py

start_basic_cli:
	pipenv run python src/cli_rag.py

run_all_cli:
	@echo "Starting Elasticsearch..."
	@make start_elastic_search_detached
	@echo "Waiting for Elasticsearch to be ready..."
	@while ! curl -s http://localhost:9200 > /dev/null; do \
		sleep 2; \
	done
	@echo "Elasticsearch is up. Ingesting data..."
	@make ingest_data
	@echo "Data ingestion complete. Starting CLI..."
	@make start_basic_cli
