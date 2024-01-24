import psycopg2
from config import password


def create_tables(cur):

    cur.execute("""
                DROP TABLE IF EXISTS all_words CASCADE;
                DROP TABLE IF EXISTS english_words CASCADE;
                DROP TABLE IF EXISTS russian_words CASCADE;
                DROP TABLE IF EXISTS user_words;
                DROP TABLE IF EXISTS users;
    """)
    conn.commit()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS english_words(
                id SERIAL PRIMARY KEY,
                word VARCHAR(60) NOT NULL UNIQUE
                );
    """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS russian_words(
                id SERIAL PRIMARY KEY,
                word VARCHAR(60) NOT NULL UNIQUE
                );
    """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS all_words(
                id SERIAL PRIMARY KEY,
                english_words_id INTEGER NOT NULL REFERENCES english_words(id),
                russian_words_id INTEGER NOT NULL REFERENCES russian_words(id)
                );
        """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
                );
        """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS user_words(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                all_words_id INTEGER NOT NULL REFERENCES all_words(id)
                );
    """)

    conn.commit()


with psycopg2.connect(database='kursovaya_db', user='postgres', password=password) as conn:
    with conn.cursor() as cur:
        create_tables(cur)
