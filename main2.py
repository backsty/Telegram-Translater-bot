import random
import logging

import telebot
from telebot import TeleBot
from telebot import StateMemoryStorage
from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup

from main import random_words_from_db
from main import random_english_words
from main import random_russian_words
from main import if_users_not_exists
from main import add_users
from main import add_word_to_dictionary
from main import delete_word_to_dictionary
from main import adding_a_word_by_the_user

from config import TOKEN


print("Telegram bot start to working...")

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Create Memory Storage
State_Storage = StateMemoryStorage()  # Храним данные в словаре
BOT = TeleBot(TOKEN, state_storage=State_Storage)

all_users_list = []
user_status = {}  # Словарь с состоянием пользователя
buttons = []
add_english_word = {}
add_russian_word = {}


def show_chat_hint(*lines):
    """
    The function takes an arbitrary number of lines and combines them into one string, separating each new line with
    a newline character.
    This can be useful for formatting output in a chat.

    :param lines: Lines to join
    :return: One string consisting of all input lines separated by a newline character
    """
    return '\n'.join(lines)


def show_translation_process(data):
    """
    The function takes a dictionary with data and returns a string representing the process of translating a word.

    :param data: Dictionary with data containing 'initial_word' and 'translate_word'
    :return: String representing the process of translating a word
    """
    return f"{data['initial_word']} -> {data['translate_word']}"


class Commands:
    """
    Class containing constants for bot commands. Each constant is a text string that the user must send to the bot
    to perform a certain command.

    ADD_WORD: Command to add a new word to the user's dictionary.
    DELETE_WORD: Command to delete a word from the user's dictionary.
    NEXT: Command to move to the next set of flashcards for learning words.
    """
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово 🗑️'
    NEXT = 'Дальше ⏩'


class States(StatesGroup):
    """
    Class containing states for the bot. Each state represents a stage in the dialogue with the bot.

    initial_word: The state in which the user enters the initial word for translation.
    translate_word: The state in which the user enters the translation of the word.
    another_word: The state in which the user can enter another word for translation.
    """
    initial_word = State()
    translate_word = State()
    another_word = State()


# Данная функция предназначена для дальнейшей реализации и сейчас не задействована!!!
def get_users_id(user_id):
    """
    The function checks whether the user exists in the database. If the user does not exist, the function adds him
    to the database and returns 0.
    If the user exists, the function returns his status.

    :param user_id: user_id
    :return: user_status
    """
    if if_users_not_exists(user_id):
        all_users_list.append(user_id)
        user_status[user_id] = 0
        print("A new user has been found!")
        return 0
    else:
        return user_status[user_id]


# Выделил в отдельную функцию т к я не понимаю почему, когда убираю not то приветственное сообщение не отправляется
@BOT.message_handler(commands=['start'])
def start(message: types.Message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    if not if_users_not_exists(chat_id):
        # Можно и раскомментировать. Опять же для дальнейшей реализации!!!
        # all_users_list.append(chat_id)
        add_users(chat_id, user_name)
        user_status[chat_id] = 0
        BOT.send_message(chat_id, f"Привет {user_name} 👋 Давай попрактикуемся в английском языке. "
                                  f"Тренировки можешь проходить в удобном для себя темпе. "
                                  f"Используй команду /cards для того чтобы начать обучение.")


# Создаём обработчик команды
@BOT.message_handler(commands=['cards'])
def create_cards(message: types.Message):
    """
    Handler for the /cards and /start commands. This function is designed to start communicating with the bot.
    It welcomes the user if he is new (that is, not yet entered into the database) and creates for him
    a set of flashcards for learning words in different languages. Each card contains one word and its translation.
    The function also tracks button clicks and saves information about the current word and its translation.

    :param message: Massage from the user
    :return: None

    Description of the functionality in stages:

    1. Checks if the user exists in the database. If not, it adds it to the database.
    2. Initializes user variables (user_status, user_id ...)
    3. Creates response markup. Adds an answer keyboard with buttons for the user to interact with the dictionary card.
    4. Extracts a random English word (initial_word) from the dictionary
    and its translation (translate_word).
    5. Also generates additional words (other_words) for multiple choice of options.
    6. Changes the position and order of the buttons so that they are displayed randomly
    (using the shuffle() function from the random library).
    7. Sends the user a message with the translated word and options to match it with the answer.
    8. Sets the user's status (user_status[chat_id]) to track his status and further interaction.
    9. Saves all data in the bot's memory to track the user's progress.

    Keyboard layout:
    1-5 flashcards -> word translations
    6 card -> "Next"
    7 card -> "Add word"
    8 card -> "Delete word"
    """
    chat_id = message.chat.id
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    other_words_buttons = []
    flag = True
    if flag:
        words = random_words_from_db(chat_id)
        initial_word = words[0]
        translate_word = words[1]
        initial_word_button = types.KeyboardButton(initial_word)
        buttons.append(initial_word_button)
        other_words = list(random_russian_words(initial_word, chat_id))
    else:
        words = random_words_from_db(chat_id)
        initial_word = words[1]
        translate_word = words[0]
        initial_word_button = types.KeyboardButton(initial_word)
        buttons.append(initial_word_button)
        other_words = list(random_english_words(initial_word, chat_id))

    for word in other_words:
        other_words_buttons.append(types.KeyboardButton(word))

    buttons.extend(other_words_buttons)
    random.shuffle(buttons)

    next_button = types.KeyboardButton(Commands.NEXT)
    add_word_button = types.KeyboardButton(Commands.ADD_WORD)
    delete_word_button = types.KeyboardButton(Commands.DELETE_WORD)
    buttons.extend([next_button, add_word_button, delete_word_button])

    keyboard_markup.add(*buttons)

    first_message = f"Выберите перевод слова:\n {translate_word}"
    # reply_markup=keyboard_markup - привязываем к сообщению клавиатуру
    BOT.send_message(message.chat.id, first_message, reply_markup=keyboard_markup)
    BOT.set_state(message.from_user.id, States.initial_word, message.chat.id)

    # Отслеживаем нажатие кнопки и ловим сообщение по нему
    with BOT.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['initial_word'] = initial_word
        data['translate_word'] = translate_word
        data['other_words'] = other_words


# Создаём обработчик команды
@BOT.message_handler(func=lambda message: message.text == Commands.NEXT)
def next_cards(message: types.Message):
    """
    Handler for the NEXT command. This function calls the create_cards function to create the next set of
    flashcards for learning words.

    :param message: Message from the user
    :return: None
    """
    create_cards(message)


# Создаём обработчик команды
@BOT.message_handler(func=lambda message: message.text == Commands.DELETE_WORD)
def delete_word(message: types.Message):
    """
    Handler for the DELETE_WORD command. This function is designed to delete a word from the user's dictionary.
    It sets the user's status to 3 and sends the user a message asking them to enter the word they would like to delete.

    :param message: Message from the user
    :return: None
    """
    user_id = message.chat.id
    user_status[user_id] = 3
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=2)
    user_hint = "Напишите какое слово вы хотели бы удалить"
    BOT.send_message(message.chat.id, user_hint, reply_markup=keyboard_markup)


# Создаём обработчик команды
@BOT.message_handler(func=lambda message: message.text == Commands.ADD_WORD)
def add_word(message: types.Message):
    """
    Handler for the ADD_WORD command. This function is designed to add a new word to the user's dictionary.
    It sets the user's status to 1 and sends the user a message asking them to enter a new English word.

    :param message: Message from the user
    :return: None
    """
    user_id = message.chat.id
    user_status[user_id] = 1
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=2)
    user_hint = "Напишите новое английское слово"
    BOT.send_message(message.chat.id, user_hint, reply_markup=keyboard_markup)


# Создаём обработчик команды
@BOT.message_handler(func=lambda message: True, content_types=['text'])
def message_processing(message: types.Message):
    """
    Handler for all text messages. This function processes all text messages from the user and
    performs the corresponding actions depending on the user's status.

    Description of the functionality in stages:

    1. Initializes the necessary variables and response markup for bot processing.
    (keyboard_markup, text, flag, user_hint)
    2. Determines the current state of the user user_status to understand how to interact with the user.
    3. If the processing status is "0" (the answer to the vocabulary card), then whether the submitted text corresponds
    to initial_word.
    Next, it provides the user with feedback and a hint based on their response.
    4. If the processing status is "1" (adding an English word), then saves the provided text as an English word
    being added.
    Next, it takes the user to the next processing state.
    5. If the processing status is equal to "2" (adding a translation into Russian), then saves the provided text as a
    Russian word.
    Next, it adds this word to the user's dictionary and provides feedback.
    6. Checks for duplicate entries in the dictionary.
    7. If the processing status is "3" (word deletion), then deletes the provided word from the user's dictionary.
    Next, it gives feedback on the successful or unsuccessful deletion of the word.
    8. Sends a reply message to the user with the appropriate prompt and feedback.
    9. Calls the next_cards function to move to the next card (stage) if the user has correctly specified the
    translation of the word.

    :param message: Message from the user
    :return: None
    """
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=2)
    text = message.text
    flag = False
    user_hint = ""
    if len(user_status) == 0 or user_status.get(message.from_user.id) == 0:
        if len(user_status) == 0:
            user_status[message.from_user.id] = 0
        with BOT.retrieve_data(message.from_user.id, message.chat.id) as data:

            print(data)  # Проверяем, что возвращает retrieve_data
            if data is not None:
                print(data.keys())  # Производим проверку ключей в словаре data
                initial_word = data['initial_word']
            else:
                print("Errors, data is None!")

            if text == initial_word:
                user_hint = show_translation_process(data)
                in_chat_text_hint = ['Отлично!❤', user_hint]
                user_hint = show_chat_hint(*in_chat_text_hint)
                flag = True
            else:
                for button in buttons:
                    if button.text == text:
                        button.text = text + '❌'
                        break
                user_hint = show_chat_hint("Допущена ошибка!",
                                           f"Постарайтесь вспомнить слово {data['translate_word']} "
                                           f"и попробовать заново!")
    elif user_status[message.from_user.id] == 1:
        add_english_word[message.from_user.id] = text
        user_hint = f"Отлично, слово {text} добавлено! Теперь введите его значение"
        user_status[message.from_user.id] = 2
    elif user_status[message.from_user.id] == 2:
        add_russian_word[message.from_user.id] = text
        user_status[message.from_user.id] = 0
        if add_word_to_dictionary(message.from_user.id, add_english_word[message.from_user.id],
                                  add_russian_word[message.from_user.id]) == 'Duplicate':
            user_hint = "Это слово уже добавлено в ваш словарь!"
        else:
            user_hint = f"Отлично! Новое слово {text} добавлено в ваш словарь!\n\n"
            user_words = adding_a_word_by_the_user(message.from_user.id)
            user_hint += "Количество ваших слов ➝ " + user_words
        add_english_word.pop(message.from_user.id)
        add_russian_word.pop(message.from_user.id)
    elif user_status[message.from_user.id] == 3:
        if not delete_word_to_dictionary(message.from_user.id, text):
            user_hint = "Данного слова нет в вашем словаре!"
        else:
            user_hint = f"Слово {text} успешно удалено!\n"
            user_words = adding_a_word_by_the_user(message.from_user.id)
            user_hint += f"Теперь в вашем словаре количество слов составляет ➝ " + user_words
        user_status[message.from_user.id] = 0

    BOT.send_message(message.chat.id, user_hint, reply_markup=keyboard_markup)
    if flag:
        next_cards(message)


if __name__ == '__main__':
    BOT.add_custom_filter(custom_filters.StateFilter(BOT))  # Фильтр состояния
    BOT.infinity_polling(skip_pending=True)  # Включаем бота в режиме non_stop
