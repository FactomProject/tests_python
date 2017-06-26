import sqlite3

def connect_to_db():
    conn = sqlite3.connect('factomd-automation1.db')
    print conn
    return conn

def create_table(conn):
    #conn.execute('DROP TABLE [IF EXISTS] entries')
    conn.execute('create table if not exists entries(chainid UNIQUE)')


def insert_to_db(conn,chainid):
    #conn.execute('SELECT chainid from entries where chainid = (?)',[str(chainid)])
    print chainid
    conn.execute('INSERT INTO entries(chainid)  VALUES (?)',[str(chainid)])
    #conn.execute('INSERT INTO entries(chainid) SELECT (?) '
                # 'WHERE NOT EXISTS (SELECT chainid FROM entries WHERE chainid = (?))',(str(chainid),str(chainid),))


def fetch_from_db(conn):
     result = conn.execute('SELECT chainid from entries')
     return result

def close_connection_to_db(conn):
    conn.close()
