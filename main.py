import config
import telebot
import data
from data import User, Queue, UserQueue
import re


bot = telebot.TeleBot(config.ACCESS_TOKEN)
conn = data.CONN


@bot.message_handler(content_types=['text'])
def handler(message):
    conn = data.create_connection(config.DB_NAME)

    pattern = r'/\w+ \w+'
    try:
        command = re.search(pattern, message.text).group().split(' ')

        if command[0] == '/new':
            Queue(command[1], message.chat.id).insert(conn)
            bot.send_message(message.chat.id, Queue.enumerate_queues(conn))

        elif command[0] == '/addme':
            id = Queue.find_by_name(conn, command[1])
            if id:
                User(message.from_user.username, message.from_user.id).insert(conn)
                UserQueue(message.from_user.id, id[0], message.date).insert(conn)

    except AttributeError:
        pattern = r'/\w+'
        try:
            command = re.search(pattern, message.text).group()

            if command == '/help':
                bot.send_message(message.chat.id, 'Hi!\nCommands:\n'
                                                  '/new - create new queue\n'
                                                  '/all - show active queues')

            elif command == '/all':
                bot.send_message(message.chat.id, Queue.enumerate_queues(conn))

        except AttributeError:
            print('bad command')

    conn.close()


if __name__ == '__main__':
    print('Hello, World!')
    data.init_db(conn)
    bot.polling(none_stop=True, interval=0)
