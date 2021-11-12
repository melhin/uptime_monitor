set -e
set -u


function create_tables() {
	echo "  Creating tables in database '$POSTGRES_DB'"
	export PGPASSWORD=$POSTGRES_PASSWORD 
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -h $POSTGRES_HOST  $POSTGRES_DB <<-EOSQL
    CREATE TABLE IF NOT EXISTS public.site (
    	id int NOT null PRIMARY KEY,
    	url text NULL,
    	current_up_status varchar NOT null,
        last_update timestamp NOT NULL
    );
    CREATE TABLE IF NOT EXISTS public.ping_status (
    	id  SERIAL PRIMARY KEY,
        site_id int,
    	up_status varchar NOT NULL,
    	created_at timestamp NOT NULL,
    	response_time float4 NOT NULL,
    	response_code varchar NULL,
    	response_header text NULL,
    	response text NULL,
        CONSTRAINT fk_site FOREIGN KEY(site_id) REFERENCES site(id) ON DELETE SET NULL
    );
EOSQL
}

create_tables