import psycopg2
from sqlCommand import CreateCashflow

from config import get_connection

conn = get_connection() # for postgre sql



# from pipeline import fetch_data

def execSql(query="", connection = conn):

    # Database connection parameters
    connection = get_connection()
    cur = connection.cursor()


    # Create table
    cur.execute(query)


    # Cleanup
    connection.commit()
    cur.close()
    connection.close()

def execSelect(query="", connection = conn):

    # Database connection parameters
    connection = get_connection()
    cur = connection.cursor()


    cur.execute("[stock].[dbo].[StockPrice]")
    rows = cur.fetchall()

    # Cleanup
    connection.commit()
    cur.close()
    connection.close()

    return rows


# # Query data
# cur.execute("SELECT * FROM people")
# rows = cur.fetchall()

# print("Data in 'people' table:")
# for row in rows:
#     print(row)

