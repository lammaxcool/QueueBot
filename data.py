import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    '''
    create a database connection to a SQLite database
    :param db_file:
    :return: connection ta an db
    '''

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, query):
    '''
    create table from a sql query
    :param conn: connection to target db
    :param query:
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
        CREATE TABLE queues(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            chat_id INTEGER NOT NULL
        )
        ''')
        # users
        queries.append(''' 
        CREATE TABLE users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL
        )
        ''')
        # user_queue
        queries.append(''' 
        CREATE TABLE user_queue(
            id INTEGER PRIMARY KEY,
            queue_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            FOREIGN KEY (queue_id) REFERENCES queue (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        for query in queries:
            create_table(conn, query)

        conn.commit()

    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    conn = create_connection('queue.db')
    init_db(conn)