import config
import telebot
import data
from data import User, Queue
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
            Queue.find_by_name(conn, command[1])
            User(message.from_user.username, message.from_user.id)


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
    # if message.text == '/help':
    #     bot.send_message(message.chat.id, 'Hi!\nCommands:\n'
    #                                       '/new - create new queue\n'
    #                                       '/all - show active queues')
    #
    # elif message.text == '/new':
    #     bot.send_message(message.chat.id, "Type queue name")
    #     bot.register_next_step_handler(message, create_queue)
    #
    # elif message.text == '/all':
    #     bot.send_message(message.chat.id, Queue.enumerate_queues(conn))
    #
    # else:
    #     bot.send_message(message.chat.id, 'I can\'t understand you :(\nTry /help')


# def create_queue(message):
#     Queue(message.text, message.chat.id).insert(conn)
#     bot.send_message(message.chat.id, Queue.enumerate_queues(conn))


if __name__ == '__main__':
    print('Hello, World!')
    data.init_db(conn)
    bot.polling(none_stop=True, interval=0)
