import sqlite3

def connect_to_db():
    conn = sqlite3.connect('factomd-automation.db')
    print conn
    return conn

def create_table(conn):
    conn.execute('drop table entries')
    conn.execute('create table entries(chainid UNIQUE)')


def insert_to_db(conn,chainid):
    #conn.execute('SELECT chainid from entries where chainid = (?)',[str(chainid)])
    conn.execute('INSERT OR IGNORE INTO entries(chainid)  VALUES (?)',[str(chainid)])


def fetch_from_db(conn):
     result = conn.execute('SELECT chainid from entries')
     return result

def close_connection_to_db(conn):
    conn.close()
