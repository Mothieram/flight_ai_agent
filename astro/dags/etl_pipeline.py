from airflow.decorators import dag, task
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
import pendulum
import json

@dag(
    dag_id='aviationstack_flight_info_dag',
    start_date=pendulum.now().subtract(days=1),
    schedule='@daily',
    catchup=False,
    tags=['aviation', 'postgres']
)
def flight_pipeline():

    @task
    def create_flight_table():
        hook = PostgresHook(postgres_conn_id='your_postgres_connection_id')
        hook.run("""
        CREATE TABLE IF NOT EXISTS flight_data (
            id SERIAL PRIMARY KEY,
            flight_date DATE,
            flight_status VARCHAR(50),
            departure_airport VARCHAR(100),
            departure_timezone VARCHAR(100),
            arrival_airport VARCHAR(100),
            arrival_timezone VARCHAR(100),
            airline_name VARCHAR(100)
        );
        """)

    extract = HttpOperator(
        task_id='extract_flight_data',
        http_conn_id='aviationstack_api',
        endpoint='v1/flights?access_key={{ conn.aviationstack_api.extra_dejson.access_key }}',
        method='GET',
        response_filter=lambda r: json.loads(r.text),
        log_response=True,
        do_xcom_push=True
    )

    @task
    def transform_flight_data(ti=None):
        response = ti.xcom_pull(task_ids='extract_flight_data')
        flights = response.get('data', [])

        cleaned_data = []
        for flight in flights:
            cleaned_data.append({
                'flight_date': flight.get('flight_date'),
                'flight_status': flight.get('flight_status'),
                'departure_airport': flight.get('departure', {}).get('airport'),
                'departure_timezone': flight.get('departure', {}).get('timezone'),
                'arrival_airport': flight.get('arrival', {}).get('airport'),
                'arrival_timezone': flight.get('arrival', {}).get('timezone'),
                'airline_name': flight.get('airline', {}).get('name')
            })

        return cleaned_data

    @task
    def load_to_postgres(flight_data):
        hook = PostgresHook(postgres_conn_id='your_postgres_connection_id')
        rows = []
        for entry in flight_data:
            rows.append((
                entry['flight_date'],
                entry['flight_status'],
                entry['departure_airport'],
                entry['departure_timezone'],
                entry['arrival_airport'],
                entry['arrival_timezone'],
                entry['airline_name']
            ))

        hook.insert_rows(
            table='flight_data',
            rows=rows,
            target_fields=[
                'flight_date',
                'flight_status',
                'departure_airport',
                'departure_timezone',
                'arrival_airport',
                'arrival_timezone',
                'airline_name'
            ],
            commit_every=100
        )

    # DAG task sequence
    create = create_flight_table()
    extract_task = extract
    transformed = transform_flight_data()
    loaded = load_to_postgres(transformed)

    create >> extract_task >> transformed >> loaded

flight_pipeline()
