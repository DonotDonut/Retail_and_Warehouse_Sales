# methods connection to main 
from methods.database import Database
from methods.sale import Sales
from methods.plot import Plot

# libraries need 
from pathlib import Path

cvs_path = Path("input_data") / "Warehouse_and_Retail_Sales.csv"

# database parameters, edit for personal database 
database_username  = ''
database_password = ''
database_host = 'localhost'
database_port = 5432
database_name  = ''

table_name = 'warehouse_and_retail_sales'

Sales.create_table('warehouse_and_retail_sales', database_username, database_password, database_host, database_port, database_name)

Database.copy_csv_to_postgres(cvs_path, database_username, database_password, database_host, database_port, database_name, table_name)

Plot.plot_item_type_sold_more_often(
        database_username,
        database_password,
        database_host,
        database_port,
        database_name,
        table_name="warehouse_and_retail_sales",
        top_n=15
    )

Plot.plot_retail_sales_by_month_year(
        database_username,
        database_password,
        database_host,
        database_port,
        database_name,
        table_name="warehouse_and_retail_sales"
    )


