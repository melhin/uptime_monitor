# Uptime Monitor

## What is this ?
A simple implementation for monitoring multiple wesites. The core principle here is by using a get request we monitor websites. The configuration is specified by db entries

## How does this work ?

### Core components and explanation

#### Scheduler:
* The scheduler is responsible for looking at the configuration and kicking of tasks. The configuration is in a site_config table. For simplicity we have specified only 4 types of schedule (1, 5, 10 minutes and 1 hour).

* In this simple implementation each schedular job (based on time) wakes up
and inserts jobs using a simple insert from select in the database.

* The scheduler is kept separately to isolate changes in scheduling. So lets say instead of 4 groups we now have more groups or custom. the triggering mechanism can be implemented the job queue is unaffected. We could look at airflow for inspiration

* The code is in site_checker/scheduler.py. Can be run from the root (if in poetry shell) using `python produce scheduler` 


#### Worker
* The worker in plain sense looks at the job queue checks websites and produces the message to kafka

* The worker is completely async inorder to effectively use asyncio for IO
requests.

* We can run multiple workers over many machines as the only requirement is a connection to the db for new jobs

* The code is in site_checker/job_consumer.py. Can be run from the root (if in poetry shell) using `python produce worker` 


#### Consumer
* Is a simple kafka consumer that takes responses of the kafka queue and then
writes them to the db

* It uses 2 tables one to register sites and another ping_status. Site has the details like url , last_updated and last status. Ping status has more detailed reporting of an individual ping

* Reports can be made out of ping_status and sites combined

* The code is in consumer/db_consume.py. Can be run from the root (if in poetry shell) using `python consumer` 


## How to Run the project ?

### Local
* A make file is provided to ease the process of running three services together

* `docker-compose.yaml` has a portion where env vars can be provided for Postgresql and Kafka connection. For ease of use it is provided with the default support values

* Firstly run the support services i.e kafka and postgresql. For this
    ```
    make start-support
    ```
    monitor logs using
    ```
    make logs-support
    ```
    Make sure both the services are up

* Then run the services
    ```
    make start
    ```
    monitor logs using
    ```
    make logs
    ```

* Now you can see the services running by the logs. But there are no schedules yet because the site_config is empty. For a sample there is a script in the utils directory .
    Run
    ```
    make load-data
    ``` 
    to enter values to site_config

    If you would like to enter more values just add more insert statements in the script `utils/create_schedule_data` and then the config would be ready

* To stop services
    ```
    make stop
    make stop-support
    ```

## Run tests
* Install poetry
*   Have an environment to run the test first
    ```
    poetry shell
    poetry install
    ```
* In the poetry shell 
    ```
    pytest
    ```
