import psycopg2
from config import password, database, user
from functools import wraps

"""
Хотел тут добавить traceback.
P.S. : Сделаю это чутка позже :)
"""
# import traceback
# import traceback_with_variables


def db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with psycopg2.connect(database=database, user=user, password=password) as conn:
            with conn.cursor() as cur:
                return func(cur, *args, **kwargs)
    return wrapper


@db_connection
# Получение случайной пары слов (одно русское, другое английское) из базы данных учитывая ассоциации пользователя
def random_words_from_db(cur, user_id):
    """
    The function selects a random word from the database for the specified user.
    It connects to the database, executes an SQL query to select a random word that has not yet been presented to the
    user, and returns this word. If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Extracts a couple of words: rus_w.word - Russian word, en_w.word - English word.
    2. Joins the russian_words table to establish associations with the Russian word.
    3. Joins the all_words table to link the Russian word with the corresponding English word.
    4. Joins the english_words table to get the English word.
    5. Uses FULL OUTER JOIN with the user_words table to activate words that may not have associations with this user.
    6. Apply the condition to account for the specified user (u_w.user_id = %s OR u_w.user_id is NULL).
    7. Sort the result randomly (ORDER BY random()).
    8. Set the result limit to 1 (LIMIT 1).

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param user_id: User ID
    :return: A random word from database, or None if no words are found or en error occurs
    """
    try:
        cur.execute("""
            SELECT rus_w.word AS rw, en_w.word AS ew
            FROM russian_words rus_w
            JOIN all_words all_w ON all_w.russian_words_id = rus_w.id
            JOIN english_words en_w ON en_w.id = all_w.english_words_id
            FULL OUTER JOIN user_words u_w ON u_w.all_words_id = all_w.id
            WHERE u_w.user_id = %s OR u_w.user_id is NULL
            ORDER BY random()
            LIMIT 1;
        """, (user_id,))
        return cur.fetchone()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Получение списка случайных английских слов из базы данных учитывая ассоциации пользователя
def random_english_words(cur, word_to_avoid, user_id):
    """
    The function selects four random English words from the database that do not match the specified word and have
    not yet been presented to the user.
    It connects to the database, executes an SQL query to select the words, and returns them as a list.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT operator, extract the English word en_w.word from the english_words table.
    2. Join the all_words table to establish an association with Russian words.
    3. Establish a FULL OUTER JOIN with the user_words table to activate words that may not have associations.
    4. Apply a condition to exclude a certain word (en_w.word!= %s). We also take into account the specified user
    (u_w.user_id = %s OR u_w.user_id is NULL)
    5. Sort the result randomly (ORDER BY random()).
    6. Set the result limit to 4 (LIMIT 4).

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param word_to_avoid: The word that should not be selected
    :param user_id: User ID
    :return: A list of four random words, or an empty list if no words are found or an error occurs
    """
    output_words = []
    try:
        cur.execute("""
            SELECT en_w.word
            FROM english_words en_w
            JOIN all_words all_w ON all_w.english_words_id = en_w.id
            FULL OUTER JOIN user_words u_w ON u_w.all_words_id = all_w.id
            WHERE en_w.word != %s AND (u_w.user_id = %s OR u_w.user_id is NULL)
            ORDER BY random()
            LIMIT 4;
        """, (word_to_avoid, user_id))
        for row_list in cur.fetchall():
            output_words.append(row_list[0])
        return output_words
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Получение списка случайных русских слов из базы данных учитывая ассоциации пользователя
def random_russian_words(cur, word_to_avoid, user_id):
    """
    The function selects four random Russian words from the database that do not match the specified word and have
    not yet been presented to the user.
    It connects to the database, executes an SQL query to select the words, and returns them as a list.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT operator, extract the Russian word rus_w.word from the russian_words table.
    2. Join the all_words table to establish an association with English words.
    3. Establish a FULL OUTER JOIN with the user_words table to activate words that may not have associations.
    4. Apply a condition to exclude a certain word (rus_w.word != %s). We also take into account the specified user
    (u_w.user_id = %s OR u_w.user_id is NULL)
    5. Sort the result randomly (ORDER BY random()).
    6. Set the result limit to 4 (LIMIT 4).

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param word_to_avoid: The word that should not be selected
    :param user_id: User ID
    :return: A list of four random words, or an empty list if no words are found or an error occurs
    """
    output_words = []
    try:
        cur.execute("""
            SELECT rus_w.word
            FROM russian_words rus_w
            JOIN all_words all_w ON all_w.russian_words_id = rus_w.id
            FULL OUTER JOIN user_words u_w ON u_w.all_words_id = all_w.id
            WHERE rus_w.word != %s AND (u_w.user_id = %s OR u_w.user_id is NULL)
            ORDER BY random()
            LIMIT 4;
        """, (word_to_avoid, user_id))
        for row_list in cur.fetchall():
            output_words.append(row_list[0])
        return output_words
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Проверка существования пользователя(id, name)
def if_users_not_exists(cur, user_id):
    """
    The function checks whether the user exists in the database.
    It connects to the database, executes an SQL query to search for a user with the specified ID, and returns True if
    the user is not found, and False if the user is found.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT statement, we check the presence of the user in the database based on the provided user_id.
    2. Extract a row from the users table, where user_id corresponds to the input data.
    3. The function returns True if the user is found, otherwise it returns False.

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param user_id: User ID
    :return: True if the user is not found, and False if the user is found
    """
    try:
        cur.execute("""
            SELECT * FROM users
            WHERE id = %s
        """, (user_id,))
        if cur.fetchone() is None:
            return True
        # if cur.fetchone() is None:
        #     return True
        # else:
        #     return False
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)
        return False


@db_connection
# В дальнейшем нужно подправить эту функцию!!!!!!!!!!!!!!!!!!
# Добавление пользователя для дальнейшего взаимодействия с ним
def add_users(cur, user_id, name):
    """
    The function adds a new user to the database.
    It connects to the database, executes an SQL query to check whether a user with the specified ID exists.
    If the user already exists, the function prints a message about this and terminates.
    If the user does not exist, the function executes an SQL query to add a new user and commits the changes.
    If an exception occurs, the function prints information about the exception.

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param user_id: User ID
    :param name: User name
    :return:
    """
    try:
        cur.execute("""
            INSERT INTO users (id, name)
            VALUES (%s, %s)
        """, (user_id, name))
        cur.connection.commit()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Добавление пар слов в словарь
def add_word_to_dictionary(cur, user_id, english_word, russian_word):
    """
    The function adds a new word to the user's dictionary in the database.
    It connects to the database and executes a series of SQL queries to add the English and Russian words to their
    respective tables, links them in the all_words table, and adds the link to the user in the user_words table.
    If an exception occurs, the function checks if it is a duplicate and returns 'Duplicate' if so.
    Otherwise, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the INSERT operator, insert the provided word - english into the english_words table, while returning
    the generated ID - english_word_id.
    2. Using the INSERT operator, insert the provided word world - Russian into the russian_words table, while returning
    the generated ID - russian_word_id.
    3. Using the INSERT operator, insert a row into the all_word table, while establishing a connection between English
    and Russian words, while returning the generated ID - all_words_id.
    4. Using the INSERT operator, insert a row into the user_word table, while associating the user word with the
    specified user.
    5. Using the conn.commit() function, we commit a transaction to save changes to the database.
    6. In exception handling, we check whether the exception contains the PostgresSQL error code '23505', which
    indicates a violation of the uniqueness of the restriction. In such situations, the function will return 'Duplicate'

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param user_id: User ID
    :param english_word: English word to add
    :param russian_word: Russian word to add
    :return:
    """
    try:
        cur.execute("""
            INSERT INTO english_words (word)
            VALUES (%s) RETURNING id
        """, (english_word,))
        english_word_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO russian_words (word)
            VALUES (%s) RETURNING id
        """, (russian_word,))
        russian_word_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO all_words (english_words_id, russian_words_id)
            VALUES (%s, %s) RETURNING id
        """, (english_word_id, russian_word_id))
        all_words_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO user_words (user_id, all_words_id)
            VALUES (%s, %s)
        """, (user_id, all_words_id))
        cur.connection.commit()
    except Exception as ex:
        if ex.pgcode == '23505':
            return 'Duplicate'
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


# Удаление пары слов из словаря
def delete_word_to_dictionary(user_id, english_word):
    """
    The function removes the specified word from the user's dictionary in the database.
    It checks the existence of the English word and its Russian equivalent in the user's dictionary,
    finds the link between them and deletes this word.
    If the word is successfully deleted, the function returns True.
    If the word is not found, the function returns False.
    If an exception occurs, the function prints information about the exception.

    :param user_id: User ID
    :param english_word: English word t delete
    :return: True if the word is successfully deleted, and False if the word is not found
    """
    try:
        english_words_id = checking_existence_english_word(user_id, english_word)
        russian_words_id = checking_existence_russian_word(user_id, english_word)
        if english_words_id is not None:
            word_id = find_connect_between_english_words(english_words_id[0])
            russian_words_id = word_id[1]
            all_words = word_id[0]
            delete_a_specific_word(all_words, english_words_id[0], russian_words_id)
            return True
        elif russian_words_id is not None and english_words_id is None:
            word_id = find_connect_between_russian_words(russian_words_id[0])
            english_words_id = word_id[1]
            all_words = word_id[0]
            delete_a_specific_word(all_words, english_words_id, russian_words_id[0])
            return True
        else:
            return False
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Удаление пользовательской пары слов
def delete_a_specific_word(cur, all_words, english_word_id, russian_word_id):
    """
    The function deletes a specific word from the database.
    It connects to the database and executes a series of SQL queries to delete the word from the user_words, all_words,
    english_words, and russian_words tables.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Defines the ID of the Russian (russian_words_id) and English (english_words_id) words, if they exist in the
    database.
    2. If an English word exists (english_words_id is not equal to None), then we find the ID of the related
    English-Russian words into words (all_words_id).
    3. Removes the word association from the database.
    Russian word exists (russian_words_id is not equal to None), then we find the ID of the related Russian-English
    words into words (all_words_id).
    5. Removes the word association from the database.

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param all_words: Word ID in the all_words table
    :param english_word_id: English word ID in the english_words table
    :param russian_word_id: Russian word ID in the russian_words table
    :return:
    """
    try:
        cur.execute("""
            DELETE FROM user_words
            WHERE all_words_id = %s
        """, (all_words,))
        cur.execute("""
            DELETE FROM all_words
            WHERE id = %s
        """, (all_words,))
        cur.execute("""
            DELETE FROM english_words
            WHERE id = %s
        """, (english_word_id,))
        cur.execute("""
            DELETE FROM russian_words
            WHERE id = %s
        """, (russian_word_id,))
        cur.connection.commit()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Проверка существования английского слова. Если существует, то выводим id
def checking_existence_english_word(cur, user_id, word):
    """
    The function checks the existence of an English word in the database.
    If the word exists, the function returns its ID.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT statement, we extract the ID en_w.id the English word (english_words) associated with the user.
    2. Using the JOIN operator, we join the all_words table to establish associations with Russian words.
    3. Using the JOIN operator, we join the user_words table to get user-specific associations.
    4. Using the WHERE operator, we apply conditions to verify that the provided user ID matches the English word.
    (u_w.user_id = %sANDen_w.ward = %s).

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param user_id: User ID
    :param word: English word to check
    :return: ID of the English word, if it exists
    """
    try:
        cur.execute("""
            SELECT en_w.id 
            FROM english_words en_w
            JOIN all_words all_w ON en_w.id = all_w.english_words_id
            JOIN user_words u_w ON u_w.all_words_id = all_w.id
            WHERE u_w.user_id = %s AND en_w.word = %s
        """, (user_id, word))
        return cur.fetchone()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Проверка существования русского слова. Если существует, то выводим id
def checking_existence_russian_word(cur, user_id, word):
    """
    The function checks the existence of a Russian word in the database.
    If the word exists, the function returns its ID.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT statement, we extract the ID en_w.id the Russian word (russian_words) associated with the user.
    2. Using the JOIN operator, we join the all_words table to establish associations with English words.
    3. Using the JOIN operator, we join the user_words table to get user-specific associations.
    4. Using the WHERE operator, we apply conditions to verify that the provided user ID and the Russian word match.
    (u_w.user_id = %s AND rus_w.word = %s).

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param user_id: User ID
    :param word: Russian word to check
    :return: ID of the Russian word, if it exists
    """
    try:
        cur.execute("""
            SELECT rus_w.id 
            FROM russian_words rus_w
            JOIN all_words all_w ON rus_w.id = all_w.russian_words_id
            JOIN user_words u_w ON u_w.all_words_id = all_w.id
            WHERE u_w.user_id = %s AND rus_w.word = %s
        """, (user_id, word))
        return cur.fetchone()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Поиск связей между английскими словами
def find_connect_between_english_words(cur, english_words_id):
    """
    The function finds connections between English words in the database.
    It returns the ID and the ID of the Russian word associated with the English word.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT operator, we extract the ID of the English-Russian word reference (all_words_id) and the ID of
    the associated Russian word russian_words_id.
    2. Using the WHERE operator, we filter the results based on the provided english_words_id to search for associations
    specific to this word.

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param english_words_id: English word ID
    :return: tuple containing ID and Russian word ID
    """
    try:
        cur.execute("""
            SELECT id, russian_words_id FROM all_words
            WHERE english_words_id = %s
        """, (english_words_id,))
        return cur.fetchone()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Поиск связей между русскими словами
def find_connect_between_russian_words(cur, russian_words_id):
    """
    The function finds connections between Russian words in the database.
    It returns the ID and the ID of the English word associated with the Russian word.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT operator, we extract the ID of the Russian-English word reference (all_words_id) and the ID of
    the associated English word english_words_id.
    2. Using the WHERE operator, we filter the results based on the provided russian_words_id to search for associations
    specific to this word.

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param russian_words_id: Russian word ID
    :return: tuple containing ID and English word ID
    """
    try:
        cur.execute("""
            SELECT id, english_words_id FROM all_words
            WHERE russian_words_id = %s
        """, (russian_words_id,))
        return cur.fetchone()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


@db_connection
# Пользователь добавляет своё слово
def adding_a_word_by_the_user(cur, user_id):
    """
    The function counts the number of words added by the user to the database.
    If an exception occurs, the function prints information about the exception.

    Explanation of the SQL query:

    1. Using the SELECT operator, we extract the number of rows in the user_words table, provided that the user_id
    corresponds to the provided user_id.

    Also, this function intercepts all exceptions that may occur during the execution of the request and outputs
    detailed information about them is available in the terminal for debugging.

    :param cur: cursor for working with the database
    :param user_id: User ID
    :return: String representation of the number of words added by the user
    """
    try:
        cur.execute("""
            SELECT count(*) FROM user_words
            WHERE user_id = %s
        """, (user_id,))
        return str(cur.fetchone()[0])
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        massage = template.format(type(ex).__name__, ex.args)
        print(massage)


#  В будущем тут будут функции по добавлению статистики пользователей и
# функция, которая будет показывать ответы пользователя и заносить их в статистику
# В виде (user_id, word_id, answer - или же ответ пользователя)
