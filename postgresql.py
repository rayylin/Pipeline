import psycopg2
from sqlCommand import CreateCashflow





# from pipeline import fetch_data

def execSql(query=""):

    # Database connection parameters
    conn = psycopg2.connect(
        host="localhost",
        # port=5432,
        dbname="pipeline",
        user="chenruijia",
        password="rebecca"
    )
    cur = conn.cursor()


    # Create table
    cur.execute(query)


    # Cleanup
    conn.commit()
    cur.close()
    conn.close()

def execSelect(query=""):

    # Database connection parameters
    conn = psycopg2.connect(
        host="localhost",
        # port=5432,
        dbname="pipeline",
        user="chenruijia",
        password="rebecca"
    )
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

