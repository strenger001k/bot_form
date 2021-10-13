import os
import telebot
from telebot import types

import database as db
from config import TOKEN
from keyboard import name, age, gender, back, info, setting, male, female


bot = telebot.TeleBot(TOKEN)

BD = {}


@bot.message_handler(commands=['start'])
def send_message(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.from_user.id, f'Привіт{message.from_user.first_name}, я бот для анкетуваня!', reply_markup=markup)
    BD[message.chat.id] = []
    msg = bot.send_message(message.from_user.id, "Ваше Ім'я")
    bot.register_next_step_handler(msg, process_name, 0)


def process_name(message, a):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if len(message.text) >= 2 and\
       len(message.text) <= 20:
        if not a:
            db.add(BD, message.chat.id, message.text)
        else:
            db.replace(BD, message.chat.id, message.text, 0)
        markup.add(back)
        msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
        if not a:
            bot.register_next_step_handler(msg, process_age, 0)
        else:
            bot.register_next_step_handler(msg, process_age, 1)
    else:
        bot.reply_to(message, "Імʼя від 2 до 20 символів")
        msg = bot.send_message(message.from_user.id, "Ваше Ім'я")
        if not a:
            bot.register_next_step_handler(msg, process_name, 0)
        else:
            bot.register_next_step_handler(msg, process_name, 1)


def process_age(message, a):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if message.text == "Назад":
        msg = bot.send_message(message.from_user.id, "Ваше Ім'я")
        bot.register_next_step_handler(msg, process_name, 1)
    else:
        if message.text.isdigit():
            if int(message.text) < 2 or\
               int(message.text) > 102:
                bot.reply_to(message, "Возраст от 2 до 102")
                msg = bot.send_message(message.from_user.id, "Ваш вік")
                if not a:
                    bot.register_next_step_handler(msg, process_age, 0)
                else:
                    bot.register_next_step_handler(msg, process_age, 1)
            else:
                if not a:
                    db.add(BD, message.chat.id, message.text)
                else:
                    try:
                        db.replace(BD, message.chat.id, message.text, 1)
                    except IndexError:
                        db.add(BD, message.chat.id, message.text)
                markup.add(male, female, back)
                msg = bot.send_message(message.from_user.id, "Стать", reply_markup=markup)
                bot.register_next_step_handler(msg, process_gender)
        else:
            bot.reply_to(message, "Ви увели не цифру. Спробуйте ще раз...")
            msg = bot.send_message(message.from_user.id, "Ваш вік")
            if not a:
                bot.register_next_step_handler(msg, process_age, 0)
            else:
                bot.register_next_step_handler(msg, process_age, 1)


def process_gender(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if message.text == "Назад":
        markup.add(back)
        msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
        bot.register_next_step_handler(msg, process_age, 1)
    elif message.text == "Чоловік" or\
         message.text == "Дівчина":
        db.add(BD, message.chat.id, message.text)
        bot.send_message(message.chat.id, "Ви пройшли реєстрацію")
        markup.add(info, setting)
        msg = bot.send_message(message.from_user.id, "Головне меню", reply_markup=markup)
        bot.register_next_step_handler(msg, process_menu)
    else:
        markup.add(male, female, back)
        msg = bot.send_message(message.from_user.id, "Оберіть правильну стать", reply_markup=markup)
        bot.register_next_step_handler(msg, process_gender)


def process_menu(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if message.text == "Інфа про мене":
        markup.add(back)
        msg = bot.send_message(message.from_user.id, f'*Імʼя*: {BD[message.chat.id][0]}\n*Вік*: {BD[message.chat.id][1]}\n*Стать*: {BD[message.chat.id][2]}', parse_mode="MarkdownV2", reply_markup=markup)
        bot.register_next_step_handler(msg, process_menu)
    elif message.text == "Настройки":
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    elif message.text == "Назад":
        markup.add(info, setting)
        msg = bot.send_message(message.from_user.id, "Головне меню", reply_markup=markup)
        bot.register_next_step_handler(msg, process_menu)


def process_change(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if message.text == 'Змінити вік':
        markup.add(back)
        msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change_age)
    elif message.text == 'Змінити стать':
        male = types.KeyboardButton('Чоловік')
        female = types.KeyboardButton('Дівчина')
        markup.add(male, female, back)
        msg = bot.send_message(message.from_user.id, "Ваш стать", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change_gender)
    elif message.text == 'Змінити Імʼя':
        markup.add(back)
        msg = bot.send_message(message.from_user.id, "Ваше Ім'я", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change_name)
    elif message.text == 'Назад':
        markup.add(info, setting)
        msg = bot.send_message(message.from_user.id, "Головне меню", reply_markup=markup)
        bot.register_next_step_handler(msg, process_menu)


def process_change_age(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if message.text == 'Назад':
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    else:
        if message.text.isdigit():
            if int(message.text) < 2 or\
               int(message.text) > 102:
                bot.reply_to(message, "Возраст от 2 до 102")
                msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
                bot.register_next_step_handler(msg, process_change_age)
            else:
                db.replace(BD, message.chat.id, message.text, 1)
                markup.add(name, age, gender, back)
                msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
                bot.register_next_step_handler(msg, process_change)
        else:
            bot.reply_to(message, "Ви увели не цифру. Спробуйте ще раз...")
            msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change_age)


def process_change_gender(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if message.text == 'Назад':
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    elif message.text == "Чоловік" or\
         message.text == "Дівчина":
        db.replace(BD, message.chat.id, message.text, 2)
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    else:
        markup.add(male, female, back)
        msg = bot.send_message(message.from_user.id, "Оберіть правильну стать", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change_gender)


def process_change_name(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if message.text == 'Назад':
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    else:
        if len(message.text) >= 2 and\
           len(message.text) <= 20:
            db.replace(BD, message.chat.id, message.text, 0)
            markup.add(name, age, gender, back)
            msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change)
        else:
            bot.reply_to(message, "Імʼя від 2 до 20 символів")
            msg = bot.send_message(message.from_user.id, "Ваше Ім'я")
            bot.register_next_step_handler(msg, process_change_name)
