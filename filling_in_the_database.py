import psycopg2
from config import password

with psycopg2.connect(database='kursovaya_db', user='postgres', password=password) as conn:
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO english_words (word)
                    VALUES
                    ('Hello'),
                    ('Apple'),
                    ('Orange'),
                    ('Pumpkin'),
                    ('Banana'),
                    ('Milk'),
                    ('Table'),
                    ('Chair'),
                    ('Water'),
                    ('Drink'),
                    ('Mango');
        """)

        cur.execute("""
                    INSERT INTO russian_words (word)
                    VALUES
                    ('Привет'),
                    ('Яблоко'),
                    ('Оранжевый'),
                    ('Тыква'),
                    ('Банан'),
                    ('Молоко'),
                    ('Стол'),
                    ('Стул'),
                    ('Вода'),
                    ('Пить'),
                    ('Манго');
        """)

        cur.execute("""
                    INSERT INTO all_words (english_words_id, russian_words_id)
                    VALUES
                    (1, 1),
                    (2, 2),
                    (3, 3),
                    (4, 4),
                    (5, 5),
                    (6, 6),
                    (7, 7),
                    (8, 8),
                    (9, 9),
                    (10, 10),
                    (11, 11);
        """)

        conn.commit()
# Далее тут будет добавлена функция чтения csv файла со словами и добавление их в базу данных
