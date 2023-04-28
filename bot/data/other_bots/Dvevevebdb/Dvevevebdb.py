import telebot
from os import listdir
import dill


with open([i for i in listdir() if '.txt' in i][0], 'rb') as f:
    tree = dill.loads(f.read())
bot = telebot.TeleBot('Xbdbdbd')


@bot.message_handler(commands=['start'])
def start(inf):
    tree[0](ind=0)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)