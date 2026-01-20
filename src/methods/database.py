
import re
import psycopg2
from sqlalchemy import create_engine
import csv

class Database:

    @staticmethod
    def get_connection(database_username, database_password, database_host, database_port, database_name):
        """
        Creates and returns a psycopg2 connection for the given database connection details.
        """
        return psycopg2.connect(
            host=database_host,
            port=database_port,
            dbname=database_name,   
            user=database_username,
            password=database_password
        )

    @staticmethod
    def get_engine(database_username, database_password, database_host, database_port, database_name):
        """
        Creates and returns a SQLAlchemy engine for the given database connection details.
        """
        database_url = (
            f"postgresql://{database_username}:{database_password}"
            f"@{database_host}:{database_port}/{database_name}"
        )
        return create_engine(database_url)

    @staticmethod
    def copy_csv_to_postgres(
        csv_path,
        database_username, database_password,
        database_host, database_port, database_name,
        table_name
    ):
        """
        Loads a CSV into Postgres using a staging table, then inserts into the final table.
        """

        def normalize_header(h: str) -> str:
            h = h.replace("\ufeff", "").strip().lower().replace("_", " ")
            h = re.sub(r"\s+", " ", h)
            return h

        conn = Database.get_connection(
            database_username, database_password,
            database_host, database_port, database_name
        )

        staging_table = f"{table_name}_staging"

        try:
            with conn, conn.cursor() as cur:
                # Read CSV header
                with open(csv_path, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    raw_header = next(reader)

                cols = [normalize_header(h) for h in raw_header]
                cols_sql = ", ".join([f'"{c}"' for c in cols])

                # Create staging table
                cur.execute(f'DROP TABLE IF EXISTS public.{staging_table};')
                cur.execute(f'CREATE TABLE public.{staging_table} (LIKE public.{table_name} INCLUDING DEFAULTS);')

                # COPY into staging
                copy_sql = f'''
                    COPY public.{staging_table} ({cols_sql})
                    FROM STDIN WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', ESCAPE '"')
                '''
                with open(csv_path, "r", encoding="utf-8", newline="") as f:
                    cur.copy_expert(copy_sql, f)

                # Debug: how many rows landed in staging?
                cur.execute(f"SELECT COUNT(*) FROM public.{staging_table};")
                staging_count = cur.fetchone()[0]
                print(f"Staging rows loaded: {staging_count}")

                # Insert into final table
                # If you DO NOT have a PK/unique constraint, remove the ON CONFLICT line.
                insert_sql = f'''
                    INSERT INTO public.{table_name} ({cols_sql})
                    SELECT {cols_sql}
                    FROM public.{staging_table}
                    ON CONFLICT DO NOTHING;
                '''
                cur.execute(insert_sql)

                # Debug: how many rows now in final?
                cur.execute(f"SELECT COUNT(*) FROM public.{table_name};")
                final_count = cur.fetchone()[0]
                print(f"Final table rows: {final_count}")

                # Cleanup staging
                cur.execute(f'DROP TABLE IF EXISTS public.{staging_table};')

            print("✅ COPY + INSERT finished.")

        finally:
            conn.close()
