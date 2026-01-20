import psycopg2
from psycopg2 import sql


class Sales:

    @staticmethod
    def create_table(name, database_username, database_password, database_host, database_port, database_name):
        """
        Create a yearly sales table (e.g., "2017_sales") if it does not already exist.
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=database_host,
                port=database_port,
                dbname=database_name,
                user=database_username,
                password=database_password,
            )

            table_name = f"{name}_sales"  # e.g. 2017_sales

            create_table_sql = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    "year"               integer, -- calendar year of the record (e.g., 2020)
                    "month"              integer, -- month number (1–12)
                    "supplier"           text,    -- supplier or distributor name
                    "item code"          text,    -- unique item/product code (can be alphanumeric)
                    "item description"   text,    -- description of the item
                    "item type"          text,    -- category/type of item (e.g., wine)
                    "retail sales"       numeric(12,2), -- units sold via retail (CSV may contain 0.00)
                    "retail transfers"   numeric(12,2), -- units transferred at retail level
                    "warehouse sales"    numeric(12,2)  -- units sold via warehouse
                );
            """).format(sql.Identifier(table_name))

            with conn.cursor() as cur:
                cur.execute(create_table_sql)

            conn.commit()
            print(f"✅ {table_name} created successfully.")

        except Exception as e:
            if conn is not None:
                conn.rollback()
            print("Error creating table:", e)

        finally:
            if conn is not None:
                conn.close()


   