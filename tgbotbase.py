# -*- coding: utf-8 -*-
import sqlite3
import telebot
from datetime import datetime
from telebot import types

bot = telebot.TeleBot('7629937536:AAHFIj1rCDsaJYboCluTe0VM8VCW1KssLt8')  # ← ВСТАВЬ свой токен сюда

ADMIN_LOGIN = 'EMRX94'
ADMIN_PASSWORD = 'ferllSEE373737'

def init_db():
    conn = sqlite3.connect('bazadanix.sql')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        pass TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Команда /start
@bot.message_handler(commands=['start'])
def show_info(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("➕ Новая запись", callback_data="new"),
        types.InlineKeyboardButton("🔍 Проверить", callback_data="check"),
        types.InlineKeyboardButton("🗑 Удалить всё", callback_data="delet")
    )
    bot.send_message(message.chat.id,
        '👋 Тут хранится база данных от EMRX \n'
        '👨‍💻 Моя группа https://t.me/emrx94chat \n'
        '📌 Или нажмите одну из кнопок ниже:', reply_markup=markup)

# Кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'new':
        start_register(call.message)
    elif call.data == 'check':
        check_data(call.message)
    elif call.data == 'delet':
        start_deletion(call.message)

# ➕ Регистрация нового пользователя
@bot.message_handler(commands=['new'])
def start_register(message):
    bot.send_message(message.chat.id, '🔑 Введите логин администратора:')
    bot.register_next_step_handler(message, verify_admin_for_new)

def verify_admin_for_new(message):
    login = message.text.strip()
    bot.send_message(message.chat.id, '🔐 Введите пароль администратора:')
    bot.register_next_step_handler(message, continue_register, login)

def continue_register(message, login):
    password = message.text.strip()
    if login == ADMIN_LOGIN and password == ADMIN_PASSWORD:
        bot.send_message(message.chat.id, 'Введите логин пользователя:')
        bot.register_next_step_handler(message, user_name)
    else:
        bot.send_message(message.chat.id, '❌ Неверный логин или пароль.')

def user_name(message):
    name = message.text.strip()
    if not name:
        bot.send_message(message.chat.id, '❗ Логин не может быть пустым')
        return
    bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(message, user_pass, name)

def user_pass(message, name):
    password = message.text.strip()
    if not password:
        bot.send_message(message.chat.id, '❗ Пароль не может быть пустым')
        return
    bot.send_message(message.chat.id, 'Введите email:')
    bot.register_next_step_handler(message, user_email, name, password)

def user_email(message, name, password):
    email = message.text.strip()
    if not email:
        bot.send_message(message.chat.id, '❗ Email не может быть пустым')
        return
    bot.send_message(message.chat.id, 'Введите телефон:')
    bot.register_next_step_handler(message, user_phone, name, password, email)

def user_phone(message, name, password, email):
    phone = message.text.strip()
    if not phone:
        bot.send_message(message.chat.id, '❗ Телефон не может быть пустым')
        return
    bot.send_message(message.chat.id, 'Введите название аккаунта:')
    bot.register_next_step_handler(message, user_location, name, password, email, phone)

def user_location(message, name, password, email, phone):
    location = message.text.strip()
    if not location:
        bot.send_message(message.chat.id, '❗ Название аккаунта не может быть пустым')
        return
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('bazadanix.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name, pass, email, phone, location, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (name, password, email, phone, location, created_at))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, '✅ Регистрация завершена. Используйте /check для проверки.')

# 🔍 Проверка пользователя
@bot.message_handler(commands=['check'])
def check_data(message):
    bot.send_message(message.chat.id, '🔑 Введите логин администратора:')
    bot.register_next_step_handler(message, check_admin_for_check)

def check_admin_for_check(message):
    login = message.text.strip()
    bot.send_message(message.chat.id, '🔐 Введите пароль администратора:')
    bot.register_next_step_handler(message, get_password_for_check, login)

def get_password_for_check(message, login):
    password = message.text.strip()

    if login != ADMIN_LOGIN or password != ADMIN_PASSWORD:
        bot.send_message(message.chat.id, '❌ Неверный логин или пароль.')
        return

    conn = sqlite3.connect('bazadanix.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    conn.close()

    if users:
        for user in users:
            bot.send_message(message.chat.id,
                f'🧾 Пользователь:\n'
                f'Логин: {user[1]}\nПароль: {user[2]}\nEmail: {user[3]}\n'
                f'Телефон: {user[4]}\nАккаунт: {user[5]}\nДата: {user[6]}')
    else:
        bot.send_message(message.chat.id, '⚠️ База данных пуста.')

# 🗑 Удаление всех данных
@bot.message_handler(commands=['delet'])
def start_deletion(message):
    bot.send_message(message.chat.id, '🔑 Введите логин администратора:')
    bot.register_next_step_handler(message, check_admin_login)

def check_admin_login(message):
    login = message.text.strip()
    bot.send_message(message.chat.id, '🔐 Введите пароль администратора:')
    bot.register_next_step_handler(message, check_admin_password, login)

def check_admin_password(message, login):
    password = message.text.strip()
    if login == ADMIN_LOGIN and password == ADMIN_PASSWORD:
        bot.send_message(message.chat.id, '⚠️ Напишите ПОДТВЕРЖДАЮ чтобы удалить все записи:')
        bot.register_next_step_handler(message, confirm_delete)
    else:
        bot.send_message(message.chat.id, '❌ Неверный логин или пароль.')

def confirm_delete(message):
    if message.text.strip().upper() == 'ПОДТВЕРЖДАЮ':
        conn = sqlite3.connect('bazadanix.sql')
        cur = conn.cursor()
        cur.execute('DELETE FROM users')
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, '🗑️ Все данные удалены.')
    else:
        bot.send_message(message.chat.id, '❌ Удаление отменено.')

# Запуск бота
bot.polling(none_stop=True)
