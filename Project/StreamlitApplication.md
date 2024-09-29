# Streamlit Application

## Containerization
The application consists of the following services
* ```elasticsearch```
    - Elasticsearch 8.4.3
    - Single-node setup
    - 5GB memory limit, 2GB JVM heap
    - Ports: 9200, 9300
* ```postgres```
     - PostgreSQL 13
     - Configurable database, user, password
     - Port: 5432 (configurable)
* ```init```
    - Custom initialization service
    - Runs only with "init" profile
    - Depends on elasticsearch and postgres
* ```streamlit```
    - Custom Streamlit application
    - Depends on init service
    - Port: 8501 (configurable)
* ```grafana```
    - Latest Grafana image
    - Port: 3000
    - Configurable admin password
    - Pre-configured dashboard
* ```ollama```
    - Latest Ollama image
    - Port: 11434
    - We can pull different models to serve them later

All services use named volumes for data persistence.

## Code

## Ingestion

The ingestion is executed using ```ìnit``` container that calls a [script](src/initializing_application.py) (that also creates a database and auser with granted permissions).In its turn this script uses an async ingestion to an Elastic Search using [script](src/data_ingestion.py)

## Monitoring

```grafana``` service is reponsible for the application online monitoring. The default  dashboard is configured in [the corresponding folder](./grafana/). The following metrics are monitored:
1. Average clarity for different models
2. Overall Score Distribution.
3. Thumbs Up/Down Statistics.
4. Relevance counts
5. Response time panel.

Metrics 1, 2, 4 are calculated using [llm-as-a-judge](./src/judge_llm.py), the 3rd metric is a feedback from a user. The 5th metric is a characteristics of a RAG/Application.

To gather statistics quicker [a script](./src/create_artificial_data.py) that creates an artificial data and ingests it to the DB has been used.

## Reproducibility

One needs only to
0. have Docker on a computer.
1. define an own ```.env``` file, that is similar to ```dev.env```.
2. execute from a root folder 
    ```bash
    chmod +x start.sh
    ./start.sh
    ```
3. wait until all services are up and the ingestion has been executed (Remark: unfortunately the _depens-on_ function od docker does NOT gurantee the correct order of container execution, one needs to work with definition of healthiness of a service, but I dont have time for this)
4. go to 8501 port on localhost and enjoy the applciation.
_Remark: _ The code dependencies are defined in Pipfile/Pipfile.lock.
_Remark:_ Sometimes changes graffan service the UUID of a data source, than one needs to go to the corresponding JSON definition of a dashboard and change th UUID on the new UUID of the current data source.

## Deployment to the cloud



