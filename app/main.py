import telebot
import requests
import re
import config
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
from db import session, CurList

bot = telebot.TeleBot(config.TOKEN)


def modified_recently():
    all_rows = session.query(CurList).all()
    if all_rows is None:
        session.close()
        return
    if datetime.now() - timedelta(minutes=10) <= all_rows[0].seen:
        session.close()
        return all_rows
    else:
        session.query(CurList).delete()
        session.commit()
        session.close()
        return


def get_currency(*args):
    lst = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
    lst = list(lst.json().values())[0]
    print(lst)
    if args:
        return lst.get(args[0])

    else:
        string = ''
        for key, value in lst.items():
            newCur = CurList(currency=key, rate=value)
            session.add(newCur)
            string += '{0} : {1}\n'.format(key, round(value, 2))
        session.commit()
        all_rows = session.query(CurList).all()
        session.close()
        return all_rows


def db_objects(all_rows):
    string = ''
    print(f'46{all_rows}')
    for row in all_rows:
        print(row)
        string += '{0} : {1}\n'.format(row.currency, round(row.rate, 2))
    return string


def drawing_plot(x, y):
    plt.plot(x, y)
    plt.savefig('test.png')
    return


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hiya, there you can check currency and ')


@bot.message_handler(commands=['history'])
def get_cur_history(message):
    days = int(re.findall('[\d]+', message.text)[0])
    currencies = re.findall("(\w+)/(\w+)", message.text)[0]
    params = {
        'start_at': date.today() - timedelta(days),
        'end_at': date.today(),
        'base': currencies[0],
        'symbols': currencies[1]
    }
    history = requests.get('https://api.exchangeratesapi.io/history', params=params)
    lst = list(history.json().values())[0]
    x = lst.keys()
    y = [val for dictionary in lst.values() for val in dictionary.values()]
    drawing_plot(x, y)
    bot.send_photo(message.chat.id, photo=open('test.png', 'rb'))


@bot.message_handler(commands=['exchange'], content_types=['text'])
def exchange_to(message):
    amount = int(re.findall('[\d]+|$', message.text)[0])
    currency = re.findall("to (\w+)|$", message.text)[0]
    currency_now = get_currency(currency)
    if currency_now:
        bot.send_message(message.from_user.id, round(amount * currency_now, 2))
    else:
        bot.send_message(message.from_user.id, 'Вибачте, ця валюта мені не відома :(')


@bot.message_handler(commands=['lst'])
def latest_cur_lst(message):
    rows = modified_recently()
    if not rows:
        rows = get_currency()
    string = db_objects(rows)
    bot.send_message(message.chat.id, string)


if __name__ == '__main__':
    bot.polling()
