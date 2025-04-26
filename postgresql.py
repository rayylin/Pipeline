import psycopg2
from sqlCommand import CreateCashflow

from config import get_connection

conn = get_connection()



# from pipeline import fetch_data

def execSql(query=""):

    # Database connection parameters
    conn = get_connection()
    cur = conn.cursor()


    # Create table
    cur.execute(query)


    # Cleanup
    conn.commit()
    cur.close()
    conn.close()

def execSelect(query=""):

    # Database connection parameters
    conn = get_connection()
    cur = conn.cursor()


    cur.execute("SELECT * FROM stockPrice")
    rows = cur.fetchall()

    # Cleanup
    conn.commit()
    cur.close()
    conn.close()

    return rows


# # Query data
# cur.execute("SELECT * FROM people")
# rows = cur.fetchall()

# print("Data in 'people' table:")
# for row in rows:
#     print(row)

