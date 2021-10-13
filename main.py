import os
import telebot
import database
from telebot import types
from flask import Flask, request

TOKEN = '934192564:AAEarOdHI04prnI9isem-FN_XJSeEefPaU8'
APP_URL = f'https://zheniabot-form.herokuapp.com/{TOKEN}'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

BD = {}

age = types.KeyboardButton('Змінити вік')
gender = types.KeyboardButton('Змінити стать')
name = types.KeyboardButton('Змінити Імʼя')
back = types.KeyboardButton('Назад')
info = types.KeyboardButton('Інфа про мене')
setting = types.KeyboardButton('Настройки')
male = types.KeyboardButton('Чоловік')
female = types.KeyboardButton('Дівчина')

@bot.message_handler(commands=['start'])
def send_message(message):
    markup =  types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.from_user.id, f"Привіт {message.from_user.first_name}, я бот для анкетуваня! ", reply_markup=markup)
    chat_id = message.chat.id
    BD[chat_id] = []
    msg = bot.send_message(message.from_user.id, "Ваше Ім'я")
    bot.register_next_step_handler(msg, process_name, 0)

def process_name(message, a):
    try:
        if(len(message.text) >= 2 and len(message.text)<=20):
            if not a:
                database.add(BD, message.chat.id, message.text)
            else:
                database.replace(BD, message.chat.id, message.text, 0)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
            markup.add(back)
            msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
            if a==0:
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
    except:
        bot.reply_to(message, "Помилка(")

def process_age(message, a):
    if message.text == "Назад":
        msg = bot.send_message(message.from_user.id, "Ваше Ім'я")
        bot.register_next_step_handler(msg, process_name, 1)
    else:
        try:
            int(message.text)
            if (int(message.text)<2 or int(message.text)>102):
                bot.reply_to(message, "Возраст от 2 до 102")
                msg = bot.send_message(message.from_user.id, "Ваш вік")
                if not a:
                    bot.register_next_step_handler(msg, process_age, 0) 
                else:
                    bot.register_next_step_handler(msg, process_age, 1)
            else:
                if not a:
                    database.add(BD, message.chat.id, message.text)
                else:
                    try:
                        database.replace(BD, message.chat.id, message.text, 1)
                    except:
                        database.add(BD, message.chat.id, message.text)
                markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
                markup.add(male, female, back)
                msg = bot.send_message(message.from_user.id, "Стать", reply_markup=markup)
                bot.register_next_step_handler(msg, process_gender)
        except:
            bot.reply_to(message, "Ви увели не цифру. Спробуйте ще раз...")
            msg = bot.send_message(message.from_user.id, "Ваш вік")
            if not a:
                bot.register_next_step_handler(msg, process_age, 0) 
            else:
                bot.register_next_step_handler(msg, process_age, 1)

def process_gender(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    if message.text == "Назад":
        markup.add(back)
        msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
        bot.register_next_step_handler(msg, process_age, 1)
    elif message.text == "Чоловік" or message.text == "Дівчина":
        try:
            database.add(BD, message.chat.id, message.text)
            bot.send_message(message.chat.id, "Ви пройшли реєстрацію")
            markup.add(info, setting)
            msg = bot.send_message(message.from_user.id, "Головне меню", reply_markup=markup)
            bot.register_next_step_handler(msg, process_menu)
        except:
            bot.reply_to(message, "Помилка(")
    else:
        markup.add(male, female, back)
        msg = bot.send_message(message.from_user.id, "Оберіть правильну стать", reply_markup=markup)
        bot.register_next_step_handler(msg, process_gender)

    
def process_menu(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    try:
        chat_id = message.chat.id
        if message.text == "Інфа про мене":
            markup.add(back)
            msg = bot.send_message(message.from_user.id, f'*Імʼя*: {BD[chat_id][0]}\n*Вік*: {BD[chat_id][1]}\n*Стать*: {BD[chat_id][2]}', parse_mode="MarkdownV2", reply_markup=markup)
            bot.register_next_step_handler(msg, process_menu)
        elif message.text == "Настройки":
            markup.add(name, age, gender, back)
            msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change)
        elif message.text == "Назад":
            markup.add(info, setting)
            msg = bot.send_message(message.from_user.id, "Головне меню", reply_markup=markup)
            bot.register_next_step_handler(msg, process_menu)
    except:
        bot.reply_to(message, "Помилка(")
        
def process_change(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
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
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    if message.text == 'Назад':
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    else:
        try:
            int(message.text)
            if (int(message.text)<2 or int(message.text)>102):
                bot.reply_to(message, "Возраст от 2 до 102")
                msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
                bot.register_next_step_handler(msg, process_change_age)
            else:
                database.replace(BD, message.chat.id, message.text, 1)
                markup.add(name, age, gender, back)
                msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
                bot.register_next_step_handler(msg, process_change)
        except:
            bot.reply_to(message, "Ви увели не цифру. Спробуйте ще раз...")
            msg = bot.send_message(message.from_user.id, "Ваш вік", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change_age)

def process_change_gender(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    if message.text == 'Назад':
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    elif message.text == "Чоловік" or message.text == "Дівчина":
        try:
            database.replace(BD, message.chat.id, message.text, 2)
            markup.add(name, age, gender, back)
            msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change)
        except:
            bot.reply_to(message, "Помилка(")
    else:
        markup.add(male, female, back)
        msg = bot.send_message(message.from_user.id, "Оберіть правильну стать", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change_gender)

def process_change_name(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    if message.text == 'Назад':
        markup.add(name, age, gender, back)
        msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
        bot.register_next_step_handler(msg, process_change)
    else:
        try:
            if(len(message.text) >= 2 and len(message.text)<=20):
                database.replace(BD, message.chat.id, message.text, 0)
                markup.add(name, age, gender, back)
                msg = bot.send_message(message.from_user.id, "Оберіть пункт що хочете змінити", reply_markup=markup)
                bot.register_next_step_handler(msg, process_change)
            else:
                bot.reply_to(message, "Імʼя від 2 до 20 символів")
                msg = bot.send_message(message.from_user.id, "Ваше Ім'я")
                bot.register_next_step_handler(msg, process_change_name)
        except:
            bot.reply_to(message, "Помилка(")

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200

@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))