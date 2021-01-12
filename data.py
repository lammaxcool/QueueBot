import sqlite3
from sqlite3 import Error
import config


class User:
    def __init__(self, username, user_id):
        self.username = username
        self.user_id = user_id

    def insert(self, conn):
        try:
            c = conn.cursor()
            c.execute('''
            INSERT INTO users(username, user_id) VALUES (?, ?)
            ''', (self.username, self.user_id))
        except Error as e:
            print(e)


class Queue:
    def __init__(self, name, chat_id):
        self.name = name
        self.chat_id = chat_id

    def insert(self, conn):
        try:
            c = conn.cursor()
            c.execute('''
            INSERT INTO queues(name, chat_id) VALUES (?, ?)
            ''', (self.name, self.chat_id))
            conn.commit()
        except Error as e:
            print(e)

    @classmethod
    def enumerate_queues(cls, conn):
        try:
            c = conn.cursor()
            res = 'Active queues:\n'
            for name in c.execute(''' SELECT name FROM queues'''):
                res += name[0] + '\n'

            return res

        except Error as e:
            print(e)

    @classmethod
    def find_by_name(cls, conn, name):
        try:
            c = conn.cursor()
            res = c.execute(''' EXISTS (SELECT id FROM queues WHERE ? = queues.name)''', name)
            return res

        except Error as e:
            print(e)


def create_connection(db_file):
    '''
    create a database connection to a SQLite database
    :param db_file: name of db file
    :return: connection ta an db
    '''

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print('sqlite3 version: ', sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, query):
    '''
    create table from a sql query
    :param conn: connection to target db
    :param query: SQL query for creating table
    :return: None
    '''

    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)


def init_db(conn):
    queries = []
    if conn:
        # queue
        queries.append(''' 
        CREATE TABLE IF NOT EXISTS queues(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            chat_id INTEGER NOT NULL
        )
        ''')
        # users
        queries.append(''' 
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            user_id INTEGER NOT NULL
        )
        ''')
        # user_queue
        queries.append(''' 
        CREATE TABLE IF NOT EXISTS user_queue(
            id INTEGER PRIMARY KEY,
            queue_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (queue_id) REFERENCES queue (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        for query in queries:
            create_table(conn, query)

    else:
        print("Error! cannot create the database connection.")


CONN = create_connection(config.DB_NAME)

if __name__ == '__main__':
    conn = create_connection('queue.db')
    init_db(conn)
