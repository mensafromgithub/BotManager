from cryptography.fernet import Fernet
from data import db_session
from data.mint import Mint
from data.bots import Bots
from data.ans import Ans
from data.Tree2 import Tree, Twig
import dill
import telebot
import os
import shutil

TOKEN = '6171056025:AAE6O5wWoND-VRgROyRCaRjQXI7y_IJgSAg'
bot = telebot.TeleBot(TOKEN)
bot.set_my_commands([
    telebot.types.BotCommand("/start", "Перезапуск бота"),
    telebot.types.BotCommand("/help", "Помощь"),
    telebot.types.BotCommand("/blist", "Список зарегестрированных ботов"),
    telebot.types.BotCommand("/add_bot", "Зарегестрировать бота"),
    telebot.types.BotCommand("/delete_bot", "Удалить бота"),
    telebot.types.BotCommand("/add_instructions", "Добавить инструкции боту"),
    telebot.types.BotCommand("/inslist", "Ветки бота"),
    telebot.types.BotCommand("/download", "Скачать бота"),
    telebot.types.BotCommand("/change_bots_token", "Изменить токен бота"),
    telebot.types.BotCommand("/edit_mode", "Режим редактирования бота")])


@bot.message_handler(commands=['start'])
def start(inf):
    bot_help(inf)
    db_sess = db_session.create_session()
    user = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()
    if not user:
        mint = Mint()
        mint.name = inf.from_user.first_name
        mint.user_id = inf.from_user.id
        mint.cipher_key = Fernet.generate_key().decode('utf-8')
        db_sess.add(mint)
        db_sess.commit()
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="Привет!", callback_data='0'))
    keyboard.add(telebot.types.InlineKeyboardButton(text="Ого!", callback_data='1'))
    bot.send_message(inf.from_user.id, 'Привет', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def bot_help(inf):
    bot.send_message(inf.from_user.id, 'Посмотри в меню')


@bot.message_handler(commands=['blist'])
def bot_list(inf):
    db_sess = db_session.create_session()
    mint = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0]
    bot_list = db_sess.query(Bots).filter(Bots.user_id == mint.id).all()
    try:
        bot.send_message(inf.from_user.id, '\n'.join([i.name for i in bot_list]))
    except:
        bot.send_message(inf.from_user.id, 'У вас нет зарегестрированных ботов')


@bot.message_handler(commands=['add_bot'])
def add_bot(inf):
    bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Пришлите токен бота'), add_bot_to_db, 0)


def add_bot_to_db(inf, n):
    db_sess = db_session.create_session()
    if not n:
        us_id = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0].id
        bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Пришли имя'), add_bot_to_db,
                                       Bots(token=inf.text, user_id=us_id))
    else:
        os.mkdir(f"data/other_bots/{inf.text}")
        os.mkdir(f"data/other_bots/{inf.text}/data")
        shutil.copyfile('data/Tree2.py', f"data/other_bots/{inf.text}/data/Tree2.py")
        with open(f'data/other_bots/{inf.text}/{inf.text}.txt', 'wb') as f:
            tree = Tree()
            tree.make_twig(name='First twig')
            f.write(dill.dumps(tree))
        make_py(inf.text, n.token)
        cipher_key = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0].cipher_key.encode('utf-8')
        cipher = Fernet(cipher_key)
        n.name = inf.text
        n.token = cipher.encrypt(n.token.encode('utf-8')).decode('utf-8')
        db_sess.add(n)
        db_sess.commit()
        bot.send_message(inf.from_user.id, 'Бот успешно зарегестрирован')


"""@bot.callback_query_handler(func=lambda call: True)
def but_hend(inf):
    print(inf.data)"""


@bot.message_handler(commands=['add_instructions'])
def add_instructions(inf):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    db_sess = db_session.create_session()
    mint = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0]
    bot_list = db_sess.query(Bots).filter(Bots.user_id == mint.id).all()
    for n in bot_list:
        keyboard.add(telebot.types.InlineKeyboardButton(text=str(n.name)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад'))
    bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Выберите бота', reply_markup=keyboard),
                                   get_new_ins, n=0)


def get_new_ins(inf, m=None, n=None):
    if inf.text != 'Назад':
        if not n:
            with open(f'data/other_bots/{inf.text}/{inf.text}.txt', 'rb') as f:
                tree = dill.loads(f.read())
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for i in range(len(tree)):
                keyboard.add(telebot.types.InlineKeyboardButton(text=str(tree[i].name)))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Новая ветка'))
            bot.register_next_step_handler(
                bot.send_message(inf.from_user.id, 'Выберите ветку (twig)', reply_markup=keyboard),
                get_new_ins, m=inf.text, n=1)
        elif n == 1:
            if inf.text != 'Новая ветка':
                keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                keyboard.add(telebot.types.InlineKeyboardButton(text='twig'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='text'))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Назад'))
                bot.register_next_step_handler(
                    bot.send_message(inf.from_user.id, 'Выберите тип сообщения', reply_markup=keyboard),
                    get_new_ins, m=[inf.text, m], n=2)
            else:
                bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Пришлите название ветки'),
                                               add_instructions_to_bot, m=['twig', m])
        elif n == 2:
            if inf.text == 'text':
                bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Пришлите сообщение'),
                                               add_instructions_to_bot, m=[inf.text, *m])
            elif inf.text == 'twig':
                with open(f'data/other_bots/{m[-1]}/{m[-1]}.txt', 'rb') as f:
                    tree = dill.loads(f.read())
                keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                signals = tree[m[0]].signals.copy()
                print(signals)
                del signals[len(signals) - 1]
                print(signals)
                mes_list = [f"{v} {signals[i][0][0]['text'][:10]}..." if not isinstance(signals[i], Twig) else f'{v} {signals[i].name}' for v, i in enumerate(signals)]
                for i in range(len(mes_list)):
                    keyboard.add(telebot.types.InlineKeyboardButton(text=str(i)))
                keyboard.add(telebot.types.InlineKeyboardButton(text='Назад'))

                bot.send_message(inf.from_user.id, '\n\n'.join(mes_list), reply_markup=keyboard)
                bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Пришлите номер сообщения'),
                                               get_new_ins, m=[inf.text, *m], n=3)
        elif n == 3:
            if inf.text != 'Назад':
                m.insert(-1, inf.text)
                bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Пришлите название ветки'),
                                               add_instructions_to_bot, m=[*m])


def add_instructions_to_bot(inf, m=None):
    print(inf.text, m)
    with open(f'data/other_bots/{m[-1]}/{m[-1]}.txt', 'rb') as f:
        tree = dill.loads(f.read())
        if m[0] == 'text':
            tree[m[1]].make_metre(inf)
        elif m[0] == 'twig':
            if len(m) != 4:
                tree.make_twig(name=str(inf.text))
            else:
                tree.make_twig(name=f'{inf.text} ({m[1]})')
                print(tree[m[1]])
                tree[m[1]].add_metre(tree[f'{inf.text} ({m[1]})'], int(m[-2]))
        with open(f'data/other_bots/{m[-1]}/{m[-1]}.txt', 'wb') as f:
            f.write(dill.dumps(tree))
    db_sess = db_session.create_session()
    ubot = db_sess.query(Bots).filter(Bots.name == m[-1]).all()[0]
    ubot.instructions = f'data/other_bots/{m[-1]}/{m[-1]}.txt'
    db_sess.commit()
    bot.send_message(inf.from_user.id, 'Успешно')


@bot.message_handler(commands=['inslist'])
def inslist(inf):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    db_sess = db_session.create_session()
    mint = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0]
    bot_list = db_sess.query(Bots).filter(Bots.user_id == mint.id).all()
    for n in bot_list:
        keyboard.add(telebot.types.InlineKeyboardButton(text=str(n.name)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад'))
    bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Выберите бота', reply_markup=keyboard),
                                   get_ins)


def get_ins(inf):
    if inf.text != 'Назад':
        with open(f'data/other_bots/{inf.text}/{inf.text}.txt', 'rb') as f:
            tree = dill.loads(f.read())
        bot.send_message(inf.from_user.id, '\n'.join([tree[i].name for i in range(len(tree))]))


@bot.message_handler(commands=['download'])
def download(inf):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    db_sess = db_session.create_session()
    mint = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0]
    bot_list = db_sess.query(Bots).filter(Bots.user_id == mint.id).all()
    for n in bot_list:
        keyboard.add(telebot.types.InlineKeyboardButton(text=str(n.name)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад'))
    bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Выберите бота', reply_markup=keyboard),
                                   download_bot)


def make_py(name, token):
    with open(f'data/other_bots/{name}/{name}.py', 'w') as f:
        with open('data/template.txt', 'r') as t:
            template = t.read()
            f.write(template.replace('{x}', token, 1))


def download_bot(inf):
    if inf.text != 'Назад':
        shutil.make_archive(f'data/other_bots/{inf.text}/{inf.text}', 'zip', f'data/other_bots/{inf.text}')
        with open(f'data/other_bots/{inf.text}/{inf.text}.zip', 'rb') as f:
            bot.send_document(inf.from_user.id, f)
        os.remove(f'data/other_bots/{inf.text}/{inf.text}.zip')


@bot.message_handler(commands=['delete_bot'])
def delete_bot(inf):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    db_sess = db_session.create_session()
    mint = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0]
    bot_list = db_sess.query(Bots).filter(Bots.user_id == mint.id).all()
    for n in bot_list:
        keyboard.add(telebot.types.InlineKeyboardButton(text=str(n.name)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад'))
    bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Выберите бота', reply_markup=keyboard),
                                   delete_bot_from_db)


def delete_bot_from_db(inf):
    if inf.text != 'Назад':
        db_sess = db_session.create_session()
        ubot = db_sess.query(Bots).filter(Bots.name == str(inf.text)).all()[0]
        db_sess.delete(ubot)
        db_sess.commit()
        shutil.rmtree(f'data/other_bots/{inf.text}')
        bot.send_message(inf.from_user.id, 'Успешно')


@bot.message_handler(commands=['change_bots_token'])
def change_bots_token(inf):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    db_sess = db_session.create_session()
    mint = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0]
    bot_list = db_sess.query(Bots).filter(Bots.user_id == mint.id).all()
    for n in bot_list:
        keyboard.add(telebot.types.InlineKeyboardButton(text=str(n.name)))
    bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Выберите бота', reply_markup=keyboard),
                                   token_changer)


def token_changer(inf, m=None, n=None):
    if not n:
        bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Пришлите новый токен'), token_changer, m=str(inf.text), n=1)
    elif n:
        db_sess = db_session.create_session()
        print(m)
        ubot = db_sess.query(Bots).filter(Bots.name == m).all()[0]
        cipher_key = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0].cipher_key.encode('utf-8')
        cipher = Fernet(cipher_key)
        ubot.token = cipher.encrypt(inf.text.encode('utf-8')).decode('utf-8')
        bot.send_message(inf.from_user.id, 'Успешно')


@bot.message_handler(commands=['edit_mode'])
def edit_mode(inf):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    db_sess = db_session.create_session()
    mint = db_sess.query(Mint).filter(Mint.user_id == inf.from_user.id).all()[0]
    bot_list = db_sess.query(Bots).filter(Bots.user_id == mint.id).all()
    for n in bot_list:
        keyboard.add(telebot.types.InlineKeyboardButton(text=str(n.name)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад'))
    bot.register_next_step_handler(bot.send_message(inf.from_user.id, 'Выберите бота', reply_markup=keyboard),
                                   emode)


def emode(inf):
    if inf.text != 'Назад':
        with open(f'data/other_bots/{inf.text}/{inf.text}.txt', 'rb') as f:
            tree = dill.loads(f.read())
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for i in range(len(tree)):
            keyboard.add(telebot.types.InlineKeyboardButton(text=str(tree[i].name)))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Новая ветка'))
        bot.register_next_step_handler(
            bot.send_message(inf.from_user.id, 'Выберите ветку (twig)', reply_markup=keyboard),
            get_new_ins, m=inf.text, n=1)


def main():
    db_session.global_init("db/bot_data.db")
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()