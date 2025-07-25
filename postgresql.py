import psycopg2
from sqlCommand import CreateCashflow
import pyodbc
from config import get_connection, connSqlServer, connSqlServerStr

import datetime
from decimal import Decimal

#conn = get_connection() # for postgre sql

# from pipeline import fetch_data

def execSql(query="", values = (), type = "SqlServer"):

    if type == "PostgreSql":
        # Database connection parameters
        connection = get_connection()
        cur = connection.cursor()


        # Create table
        cur.execute(query)


        # Cleanup
        connection.commit()
        cur.close()
        connection.close()
    else:

        conn = pyodbc.connect(connSqlServerStr)
        cursor = conn.cursor()

        try:
            cursor.execute(query, values)
            conn.commit()
            print("Row inserted successfully.")
        except pyodbc.Error as e:
            print("Error:", e)
        finally:
            cursor.close()
            conn.close()


def execSelect(query="select * from [stock].[dbo].[StockPriceDaily]", type = "SqlServer"):
    if type == "PostgreSql":
        # Database connection parameters
        connection = get_connection()
        cur = connection.cursor()


        cur.execute(query)
        rows = cur.fetchall()

        # Cleanup
        connection.commit()
        cur.close()
        connection.close()

        return rows
    else:

        conn = pyodbc.connect(connSqlServerStr)
        cursor = conn.cursor()

        # Execute SQL query
        cursor.execute(query)

        # Fetch all results
        rows = cursor.fetchall()

        # Print results
        # for row in rows:
        #     print(row)

        # Close connection
        cursor.close()
        conn.close()

        result = []

        for row in rows:
            converted = []
            for item in row:
                if isinstance(item, datetime.datetime):
                    converted.append(item.strftime("%Y-%m-%d"))  # or item.isoformat()
                elif isinstance(item, Decimal):
                    converted.append(float(item))  # or str(item) if you prefer string
                else:
                    converted.append(item)  # int, str, etc.
            result.append(converted)

        return result


# # Query data
# cur.execute("SELECT * FROM people")
# rows = cur.fetchall()

# print("Data in 'people' table:")
# for row in rows:
#     print(row)

