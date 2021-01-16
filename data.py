import sqlite3
from sqlite3 import Error
import config
import traceback


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
            INSERT OR IGNORE INTO users(first_name, last_name, username, user_id) VALUES (?, ?, ?, ?)
            ''', (self.first_name, self.last_name, self.username, self.user_id))
            conn.commit()
        except Error:
            print(traceback.format_exc())

    @classmethod
    def find_by_username(cls, conn, username):
        try:
            c = conn.cursor()
            res = []
            for user_id in c.execute(''' SELECT user_id FROM users u WHERE ? = u.username ''', (username, )):
                res.append(user_id[0])

            return res[0] if res else None

        except Error:
            print(traceback.format_exc())

    @classmethod
    def delete(cls, conn, username):
        user_id = User.find_by_username(conn, username)
        try:
            c = conn.cursor()
            c.execute('''
            DELETE FROM users
            WHERE user_id = ?
            ''', (user_id, ))
            conn.commit()
        except Error:
            print(traceback.format_exc())
            return False

        return True


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
                users JOIN user_queue q on users.user_id = q.user_id) u 
                WHERE u.queue_id = ?
                ORDER BY u.date
            ''', (int(id), )):
                res += (user[0] + ' ' if user[0] else '')\
                       + (user[1] if user[1] else '') + ' (@' + user[2] + ')\n'

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
            for id in c.execute(''' SELECT id FROM queues WHERE ? = queues.name ''', (name, )):
                res.append(id[0])
                break

            return res[0] if res else None

        except Error:
            print(traceback.format_exc())

    @classmethod
    def delete(cls, conn, name):
        id = Queue.find_by_name(conn, name)
        try:
            c = conn.cursor()
            c.execute('''
            DELETE FROM queues
            WHERE id = ?
            ''', (id,))
            conn.commit()
        except Error:
            print(traceback.format_exc())
            return False

        return True


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

    @classmethod
    def find_by_ids(cls, conn, queue_id, user_id):
        ''' Find a row by user or queue id '''
        res = []
        try:
            c = conn.cursor()
            for id in c.execute('''
            SELECT id FROM user_queue
            WHERE user_id = ? AND queue_id = ?
            ''', (user_id, queue_id)):
                res.append(id[0])
                break
        except Error:
            print(traceback.format_exc())

        return int(res[0]) if res else None

    @classmethod
    def delete(cls, conn, queue_id, user_id):
        id = UserQueue.find_by_ids(conn, queue_id, user_id)
        if id:
            try:
                c = conn.cursor()
                c.execute('''
                DELETE FROM user_queue
                WHERE ? = id AND ? = queue_id
                ''', (id, queue_id))
                conn.commit()
                return True
            except Error:
                print(traceback.format_exc())
                return False
        else:
            return False


def create_table(conn, query):
    '''
    exec from a sql query
    :param conn: connection to target db
    :param query: SQL query for creating table
    :return: None
    '''

    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error:
        print(traceback.format_exc())


def init_db(conn):
    queries = []
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


class SQLite3Connection:
    '''
    Create a database connection to a SQLite database.
    Delete instance for closing connection.
    :param db_filename: name of db file
    '''
    def __init__(self, db_filename):
        self.conn = sqlite3.connect(db_filename)
        print('Connection created')
        # self.conn = None
        # try:
        #     self.conn = sqlite3.connect(db_filename)
        #     # print('sqlite3 version: ', sqlite3.version)
        # except Error:
        #     print(traceback.format_exc())

    def __del__(self):
        self.conn.close()
        print('Connection destroyed')

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()


if __name__ == '__main__':
    conn = SQLite3Connection(config.DB_NAME)
    init_db(conn)
    del conn