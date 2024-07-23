import psycopg2

from config import PASSWORD

conn = psycopg2.connect(dbname="postgres", user="Admin", password=f"{PASSWORD}", host="localhost")
cursor = conn.cursor()
conn.autocommit = True
sql = "CREATE DATABASE players"
cursor.execute(sql)
sql = "CREATE TABLE players (id SERIAL KEY, tg_id INT, rang NVARCHAR(30), money INT, strength INT, cock INT, equip INT)"
cursor.close()
conn.close()
