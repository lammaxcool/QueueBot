import config
import telebot

bot = telebot.TeleBot(config.ACCESS_TOKEN)


class Queue:
    counter = 0
    queues = []

    def __init__(self, name=None):
        self.name = name if name else 'queue' + str(Queue.counter)
        self.queue = []
        Queue.counter += 1
        Queue.queues.append(self)

    @staticmethod
    def check_duplicates(name):
        for queue in Queue.queues:
            if name == queue.name:
                return True

        return False

    @staticmethod
    def enumerate_queues():
        return 'Active queues:\n' + ''.join([queue.name + '\n' for queue in Queue.queues])


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, 'Hi!\nCommands:\n'
                                               '/new - create new queue\n'
                                               '/all - show active queues')

    elif message.text == '/new':
        bot.send_message(message.from_user.id, "Type queue name")
        bot.register_next_step_handler(message, create_queue)

    elif message.text == '/all':
        bot.send_message(message.from_user.id, Queue.enumerate_queues())

    else:
        bot.send_message(message.from_user.id, 'I can\'t understand you :(\nType /help')


def create_queue(message):
    Queue(message.text)
    bot.send_message(message.from_user.id, Queue.enumerate_queues())


if __name__ == '__main__':
    print('Hello, World!')
    bot.polling(none_stop=True, interval=0)
