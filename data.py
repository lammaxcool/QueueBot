import sqlite3
from sqlite3 import Error
import config
import traceback


class SQLiteError(Exception):
    ''' Raise an error with sqlite3 error '''
    pass


class User:
    def __init__(self, first_name, last_name, username, user_id):
        self.username = username
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name

    def insert(self, conn):
        try:
            c = conn.cursor()
            c.execute('''
            INSERT INTO users(first_name, last_name, username, user_id) VALUES ( ?, ?, ?)
            ''', (self.username, self.user_id))
        except Error:
            print(traceback.format_exc())


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
        except Error:
            print(traceback.format_exc())

    @classmethod
    def show_members(cls, conn, id):
        try:
            c = conn.cursor()
            res = ''
            # get queue name
            for name in c.execute(''' SELECT name FROM queues q WHERE ? = q.id''', (int(id),)):
                res += name[0] + ':\n'
                break

            # get members
            for user in c.execute('''
            SELECT u.first_name, u.last_name, u.username FROM (
                users JOIN user_queue q on users.user_id = q.user_id
                ) u WHERE u.user_id IN (
                    SELECT uq.user_id FROM user_queue uq WHERE uq.queue_id = ?
                ) ORDER BY u.date
            ''', (int(id), )):
                res += user[0] + ' ' + user[1] + '(@' + user[2] + ')\n'

            return res
        except Error:
            print(traceback.format_exc())

    @classmethod
    def enumerate_queues(cls, conn):
        try:
            c = conn.cursor()
            res = 'Active queues:\n'
            for name in c.execute(''' SELECT name FROM queues'''):
                res += name[0] + '\n'

            return res

        except Error:
            print(traceback.format_exc())

    @classmethod
    def find_by_name(cls, conn, name):
        try:
            c = conn.cursor()
            res = []
            for name in c.execute(''' SELECT id FROM queues WHERE ? = queues.name ''', (name, )):
                res.append(name[0])

            return res[0] if res else None

        except Error:
            print(traceback.format_exc())


class UserQueue:
    def __init__(self, user_id, queue_id, date):
        self.user_id = user_id
        self.queue_id = queue_id
        self.date = date

    def insert(self, conn):
        try:
            c = conn.cursor()
            c.execute('''
            INSERT INTO user_queue(user_id, queue_id, date) VALUES (?, ?, ?)
            ''', (self.user_id, self.queue_id, self.date))
            conn.commit()
        except Error:
            print(traceback.format_exc())


def create_connection(db_file):
    '''
    create a database connection to a SQLite database
    :param db_file: name of db file
    :return: connection ta an db
    '''

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        # print('sqlite3 version: ', sqlite3.version)
    except Error:
            print(traceback.format_exc())

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
    except Error:
            print(traceback.format_exc())


def init_db(conn):
    queries = []
    if conn:
        # queue
        queries.append(''' 
        CREATE TABLE IF NOT EXISTS queues(
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            chat_id INTEGER NOT NULL
        )
        ''')
        # users
        queries.append(''' 
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT NOT NULL
        )
        ''')
        # user_queue
        queries.append(''' 
        CREATE TABLE IF NOT EXISTS user_queue(
            id INTEGER PRIMARY KEY,
            queue_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            date INTEGER NOT NULL,
            FOREIGN KEY (queue_id) REFERENCES queues (id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
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
