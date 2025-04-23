import psycopg2
from sqlCommand import CreateCashflow





# from pipeline import fetch_data

def execSql(query=""):

    # Database connection parameters
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="mydb",
        user="ray",
        password="abc"
    )
    cur = conn.cursor()


    # Create table
    cur.execute(query)


    # Cleanup
    conn.commit()
    cur.close()
    conn.close()


# # Query data
# cur.execute("SELECT * FROM people")
# rows = cur.fetchall()

# print("Data in 'people' table:")
# for row in rows:
#     print(row)

