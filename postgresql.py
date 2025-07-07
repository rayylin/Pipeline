import psycopg2
from sqlCommand import CreateCashflow

from config import get_connection, connSqlServer

#conn = get_connection() # for postgre sql



# from pipeline import fetch_data

def execSql(query="", type = "SqlServer"):

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

        conn = connSqlServer
        cursor = conn.cursor()

        # Execute SQL query
        query = "SELECT * FROM table1"
        cursor.execute(query)

        # Fetch all results
        rows = cursor.fetchall()

        # Print results
        for row in rows:
            print(row)

        # Close connection
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

        conn = connSqlServer
        cursor = conn.cursor()

        # Execute SQL query
        query = "SELECT * FROM [stock].[dbo].[StockPriceDaily]"
        cursor.execute(query)

        # Fetch all results
        rows = cursor.fetchall()

        # Print results
        # for row in rows:
        #     print(row)

        # Close connection
        cursor.close()
        conn.close()

        return rows


# # Query data
# cur.execute("SELECT * FROM people")
# rows = cur.fetchall()

# print("Data in 'people' table:")
# for row in rows:
#     print(row)

