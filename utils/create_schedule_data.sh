#!/bin/bash
set -e


# This is a very boring and random script to help you insert new sites and schedules
# directly to the db. Its only purpose is to create test data

function insert_records(){
    docker exec -it uptime_monitor_db_1 bash -c "
    PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -h localhost \$POSTGRES_DB -c \"
        INSERT INTO public.site_config (url, schedule) VALUES('https://duckduckgo.com/', 'run.every_minute');
        INSERT INTO public.site_config (url, schedule) VALUES('https://google.com', 'run.every_five_minutes');
        INSERT INTO public.site_config (url, schedule) VALUES('https://bbc.com', 'run.every_ten_minutes');
    \""
}


insert_records