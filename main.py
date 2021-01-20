import config
import telebot
import data
from data import User, Queue, UserQueue, SQLite3Connection
import re


BOT = telebot.TeleBot(config.ACCESS_TOKEN)


class Handler:
    def __init__(self, conn, chat_id):
        self.conn = conn
        self.chat_id = chat_id
        # print('Handler created')

    # def __del__(self):
    #     print('Handler destroyed')

    def new(self, queue_name):
        status = Queue(queue_name, self.chat_id).insert(self.conn)
        if status:
            # BOT.send_message(self.chat_id, Queue.enumerate_queues(self.conn))
            BOT.send_message(self.chat_id, 'Successfully added "{}"'.format(queue_name))
        else:
            BOT.send_message(self.chat_id, 'Something went wrong :(\n'
                                           'Developer might be dumb...')

    def remove(self, queue_name):
        status = Queue.delete(self.conn, queue_name)
        if status:
            BOT.send_message(self.chat_id, 'Successfully removed "{}"'.format(queue_name))
        else:
            BOT.send_message(self.chat_id, 'There is no queue named "{}"'.format(queue_name))

    def addme(self, queue_name, first_name, last_name, username, user_id, date):
        queue_id = Queue.find_by_name(self.conn, queue_name)
        if queue_id:
            User(first_name,
                 last_name,
                 username,
                 user_id
                 ).insert(self.conn)
            UserQueue(user_id, queue_id, date).insert(self.conn)
        else:
            BOT.send_message(self.chat_id, 'There is no queue named "{}"'.format(queue_name))

    def delme(self, username, queue_name):
        user_id = User.find_by_username(self.conn, username)
        if not user_id:
            BOT.send_message(self.chat_id, 'You are not a member of any queue!')
            return

        # check if queue exists
        queue_id = Queue.find_by_name(self.conn, queue_name)
        if not queue_id:
            BOT.send_message(self.chat_id,
                             'There is no "{}" queue'.format(queue_name))
            return

        # check if user is member of queue and remove
        status = UserQueue.delete(self.conn, queue_id, user_id)
        if status:
            BOT.send_message(self.chat_id,
                             '@{} has been removed from "{}"'.format(username, queue_name))
        else:
            BOT.send_message(self.chat_id,
                             'You are not a member of "{}"'.format(queue_name))

    def show(self, queue_name):
        queue_id = Queue.find_by_name(self.conn, queue_name)
        if queue_id:
            BOT.send_message(self.chat_id, Queue.show_members(self.conn, queue_id))
        else:
            BOT.send_message(self.chat_id, 'There is no queue named "{}"'.format(queue_name))

    def all(self):
        BOT.send_message(self.chat_id, Queue.enumerate_queues(self.conn))

    def help(self):
        BOT.send_message(self.chat_id, 'Hi!\nCommands:\n'
                                       '/new "queue name" - create new queue\n'
                                       '/remove "queue name - remove queue\n"'                            
                                       '/show "queue name" - show queue members\n'
                                       '/all - show active queues\n'
                                       '\n'
                                       '/addme "queue name" - add me to queue\n'
                                       '/delme "queue name" - delete me from queue\n')


@BOT.message_handler(content_types=['text'])
def handler(message):
    conn = data.SQLite3Connection(config.DB_NAME)
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

            elif command[0] == '/delme':
                h.delme(message.from_user.username, command[1])

            elif command[0] == '/remove':
                h.remove(command[1])

        else:
            # search single word command
            pattern = r'/\w+'
            command = re.search(pattern, message.text).group()
            if command == '/help':
                h.help()

            elif command == '/all':
                h.all()

            else:
                BOT.send_message(h.chat_id, 'One of us is dumb :(\n'
                                            'Try /help')
                # print('bad command')


if __name__ == '__main__':
    print('Hello from QueueBot!')
    conn = SQLite3Connection(config.DB_NAME)
    data.init_db(conn)
    del conn
    BOT.polling(none_stop=True, interval=0)
