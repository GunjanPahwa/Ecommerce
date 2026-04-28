import pandas as pd
from sqlalchemy import create_engine
import urllib

df=pd.read_csv('olist_master_cleaned.csv')

connection_string = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=LAPTOP-OM8LJP9I\SQLEXPRESS;'
    r'DATABASE=olist_db;'
    r'Trusted_Connection=yes;'
)

quoted_conn_string = urllib.parse.quote_plus(connection_string)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_conn_string}")
print("begin")
df.to_sql('orders_master', con=engine, if_exists='replace', index=False)
print("done")



