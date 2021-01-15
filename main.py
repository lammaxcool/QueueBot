import config
import telebot
import data
from data import User, Queue, UserQueue
import re


BOT = telebot.TeleBot(config.ACCESS_TOKEN)
conn = data.CONN


class Handler:
    def __init__(self, conn, chat_id):
        self.conn = conn
        self.chat_id = chat_id

    def new(self, queue_name):
        Queue(queue_name, self.chat_id).insert(self.conn)
        BOT.send_message(self.chat_id, Queue.enumerate_queues(self.conn))

    def addme(self, queue_name, first_name, last_name, username, user_id, date):
        queue_id = Queue.find_by_name(conn, queue_name)
        if queue_id:
            User(first_name,
                 last_name,
                 username,
                 user_id
                 ).insert(conn)
            UserQueue(user_id, queue_id, date).insert(self.conn)
        else:
            BOT.send_message(self.chat_id, 'There is no queue named "{}"'.format(queue_name))

    def show(self, queue_name):
        queue_id = Queue.find_by_name(self.conn, queue_name)
        if queue_id:
            BOT.send_message(self.chat_id, Queue.show_members(conn, queue_id))
        else:
            BOT.send_message(self.chat_id, 'There is no queue named "{}"'.format(queue_name))

    def all(self):
        BOT.send_message(self.chat_id, Queue.enumerate_queues(conn))

    def help(self):
        BOT.send_message(self.chat_id, 'Hi!\nCommands:\n'
                                       '/new "name" - create new queue\n'
                                       '/all - show active queues\n'
                                       '/addme "queue name" - add me to queue\n'
                                       '/show "queue name" - show queue members')


@BOT.message_handler(content_types=['text'])
def handler(message):
    conn = data.create_connection(config.DB_NAME)
    h = Handler(conn, message.chat.id)

    # if there is any command in the message
    pattern = r'/\w+'
    if re.search(pattern, message.text):
        # search double word command
        pattern = r'/\w+ \w+'
        command = re.search(pattern, message.text)
        if command:
            command = command.group().split(' ')
            if command[0] == '/new':
                h.new(command[1])

            elif command[0] == '/addme':
                h.addme(command[1],
                        message.from_user.first_name,
                        message.from_user.last_name,
                        message.from_user.username,
                        message.from_user.id,
                        message.date)

            elif command[0] == '/show':
                h.show(command[1])

        else:
            # search single word command
            pattern = r'/\w+'
            command = re.search(pattern, message.text).group()
            if command == '/help':
                h.help()

            elif command == '/all':
                h.all()

            else:
                print('bad command')

    conn.close()


if __name__ == '__main__':
    print('Hello, World!')
    data.init_db(conn)
    BOT.polling(none_stop=True, interval=0)
