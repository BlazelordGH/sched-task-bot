import telebot
from telebot import types

from data.read_token import read_token

from data.reset_current_task import reset_current_task
from data.delete_task import check_task_num, delete_task
from data.get_task_list import get_task_list
from data.check_task_date import check_task_date
from data.check_task_time import check_task_time
from data.check_task_exists import check_task_exists

import schedule
import threading
import datetime
import time


bot = telebot.TeleBot(read_token('data/token.json'))
schedule_running = False
tasks_list = []
current_task = reset_current_task()
chat_id = ""

start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
create_task_btn = types.KeyboardButton("Создать задачу")
delete_task_btn = types.KeyboardButton("Удалить задачу")
view_tasks_btn = types.KeyboardButton("Список задач")
start_notifications_btn = types.KeyboardButton("Включить уведомления")
stop_notifications_btn = types.KeyboardButton("Выключить уведомления")
start_menu.add(create_task_btn, delete_task_btn, view_tasks_btn, start_notifications_btn, stop_notifications_btn)

back_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
back_btn = types.KeyboardButton("Назад")
back_menu.add(back_btn)

confirmation_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
yes_btn = types.KeyboardButton("Да")
no_btn = types.KeyboardButton("Нет")
confirmation_menu.add(yes_btn, no_btn)


def get_task_time(message):
    global current_task
    if not check_task_time(current_task["date"], message.text):
        bot.send_message(chat_id, "Упс! Некорректно введено время! Введите время в формате ЧЧ:ММ.",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_task_time)
    else:
        text = message.text.split(":")
        current_task["time"] = {"hour": int(text[0]), "minute": int(text[1])}

        if check_task_exists(current_task, tasks_list):
            bot.send_message(chat_id, "Упс! Задача с таким именем и временем уже существует.",
                             reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)
        else:
            if not check_task_date(current_task["date"]):
                bot.send_message(chat_id, "Упс! Некорректно введена дата! Попробуйте ещё раз.",
                                 reply_markup=types.ReplyKeyboardRemove())
            elif not check_task_time(current_task["date"], current_task["time"]):
                bot.send_message(chat_id, "Упс! Некорректно введено время! Попробуйте ещё раз.",
                                 reply_markup=types.ReplyKeyboardRemove())
            else:
                tasks_list.append(current_task)
                bot.send_message(chat_id, f'Задача "{current_task["name"]}" успешно создана!',
                                 reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)
        current_task = reset_current_task()


def get_task_date(message):
    if not check_task_date(message.text):
        bot.send_message(chat_id, "Упс! Некорректно введена дата! Введите дату в формате ДД.ММ.ГГГГ",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_task_date)
    else:
        text = message.text.split(".")
        current_task["date"] = {"day": int(text[0]), "month": int(text[1]), "year": int(text[2])}

        bot.send_message(chat_id, "Введите время, в которое нужно выполнить задачу, в формате ЧЧ:ММ.",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_task_time)


def get_task_name(message):
    current_task["name"] = message.text.strip()

    bot.send_message(chat_id, "Выберите дату, в которую нужно выполнить задачу, в формате ДД.ММ.ГГГГ.",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_task_date)


@bot.message_handler(commands=["start"])
def start_message(message):
    global chat_id
    if not chat_id:
        chat_id = message.from_user.id
    bot.send_message(chat_id, "Привет! Чем могу помочь?", reply_markup=start_menu)


@bot.message_handler(commands=["help"])
def help_message(message):
    global chat_id
    if not chat_id:
        chat_id = message.from_user.id
    bot.send_message(chat_id, text="Привет!\n"
                                   "Я бот, который будет напоминать тебе о задачах, которые Вам предстоит выполнить.\n"
                                   "\n"
                                   "У меня есть следующие команды:\n"
                                   "/start – открыть главное меню.\n"
                                   "/createtask – создать задачу.\n"
                                   "/deletetask – удалить задачу.\n"
                                   "/tasklist – посмотреть список задач.\n"
                                   "/notstart – включить уведомления.\n"
                                   "/notstop – выключить уведомления.\n"
                                   "\n"
                                   "Введите команду /start для начала работы.")


@bot.message_handler(commands=["createtask"])
def create_task_message(message):
    if schedule_running:
        bot.send_message(chat_id, "Нельзя создавать задачи, пока включены уведомления.")
        bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)
        return
    if len(tasks_list) >= 100:
        bot.send_message(chat_id,
                         "Вы достигли лимита по количеству задач. Удалите какую-нибудь задачу, чтобы создать новую.")
        bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)

    bot.send_message(chat_id, "Введите имя задачи.", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_task_name)


def get_task_delete_confirm(message, num):
    global tasks_list
    if message.text == "Да":
        bot.send_message(chat_id, f'Задача "{tasks_list[num - 1]["name"]}" успешно удалена!')
        tasks_list = delete_task(num, tasks_list)
        if not tasks_list:
            bot.send_message(chat_id, "Список задач пуст.")
            bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)
        else:
            bot.send_message(chat_id, f"Список текущих задач ({len(tasks_list)}/100):\n\n" + get_task_list(tasks_list))
            bot.send_message(chat_id, "Введите номер задачи, которую хотите удалить.",
                             reply_markup=back_menu)
            bot.register_next_step_handler(message, get_task_delete)
    elif message.text == "Нет":
        bot.send_message(chat_id, "Введите номер задачи, которую хотите удалить.",
                         reply_markup=back_menu)
        bot.register_next_step_handler(message, get_task_delete)
    else:
        bot.send_message(chat_id, "К сожалению, такой команды у меня нет.",
                         reply_markup=confirmation_menu)
        bot.register_next_step_handler(message, get_task_delete_confirm, num)


def get_task_delete(message):
    if message.text == "Назад":
        bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)
    elif not check_task_num(message.text, tasks_list):
        bot.send_message(chat_id, "Упс! Некорректный номер задачи! Попробуйте ещё раз.")
        bot.send_message(chat_id, f"Список текущих задач ({len(tasks_list)}/100):\n\n" + get_task_list(tasks_list),
                         reply_markup=back_menu)
        bot.register_next_step_handler(message, get_task_delete)
    else:
        bot.send_message(chat_id, "Вы уверены?", reply_markup=confirmation_menu)
        bot.register_next_step_handler(message, get_task_delete_confirm, int(message.text))


@bot.message_handler(commands=["deletetask"])
def delete_task_message(message):
    if schedule_running:
        bot.send_message(chat_id, "Нельзя удалять задачи, пока уведомления включены.")
        bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)
        return

    if not tasks_list:
        bot.send_message(chat_id, "Список задач пуст.")
        bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)
    else:
        bot.send_message(chat_id, f"Список текущих задач ({len(tasks_list)}/100):\n\n" + get_task_list(tasks_list))
        bot.send_message(chat_id, "Введите номер задачи, которую хотите удалить.",
                         reply_markup=back_menu)
        bot.register_next_step_handler(message, get_task_delete)


@bot.message_handler(commands=["tasklist"])
def task_list_message(message):
    if not tasks_list:
        bot.send_message(chat_id, "Список задач пуст.")
    else:
        bot.send_message(chat_id, f"Список текущих задач ({len(tasks_list)}/100):\n\n" + get_task_list(tasks_list))
    bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)


@bot.message_handler(commands=["notstart"])
def start_notifications_message(message):
    global schedule_running
    if schedule_running:
        bot.send_message(chat_id, "Уведомления уже включены.")
    else:
        schedule_running = True
        bot.send_message(chat_id, "Уведомления включены.")
    bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)


@bot.message_handler(commands=["notstop"])
def stop_notifications_message(message):
    global schedule_running
    if schedule_running:
        schedule_running = False
        bot.send_message(chat_id, "Уведомления выключены.")
    else:
        bot.send_message(chat_id, "Уведомления уже выключены.")
    bot.send_message(chat_id, "Чем ещё могу помочь?", reply_markup=start_menu)


@bot.message_handler(content_types=["text"])
def text_messages(message):
    global chat_id
    if not chat_id:
        chat_id = message.from_user.id

    if message.text == "Создать задачу":
        create_task_message(message)
    elif message.text == "Удалить задачу":
        delete_task_message(message)
    elif message.text == "Список задач":
        task_list_message(message)
    elif message.text == "Включить уведомления":
        start_notifications_message(message)
    elif message.text == "Выключить уведомления":
        stop_notifications_message(message)
    else:
        bot.send_message(chat_id, "К сожалению, такой команды у меня нет. Чем могу помочь?",
                         reply_markup=start_menu)


def notification():
    global tasks_list, schedule_running

    if not schedule_running: return

    tasks_done = []
    for i in range(len(tasks_list)):
        current_time = datetime.datetime.now()
        if tasks_list[i]["date"]["year"] == current_time.year \
                and tasks_list[i]["date"]["month"] == current_time.month and tasks_list[i]["date"][
            "day"] == current_time.day \
                and tasks_list[i]["time"]["hour"] == current_time.hour and tasks_list[i]["time"][
            "minute"] == current_time.minute:
            bot.send_message(chat_id, text=f'Настало время выполнить задачу "{tasks_list[i]["name"]}"!')
            tasks_done.append(i + 1)
    for i in range(len(tasks_done) - 1, -1, -1):
        tasks_list = delete_task(tasks_done[i], tasks_list)


def schedule_func():
    schedule.every(1).seconds.do(notification)
    while True:
        time.sleep(1)
        schedule.run_pending()


if __name__ == "__main__":
    threading.Thread(target=schedule_func).start()
    bot.infinity_polling()
