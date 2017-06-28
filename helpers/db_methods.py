import sqlite3

def connect_to_db():
    conn = sqlite3.connect('factomd-automation25k.db')
    return conn

def create_table(conn):
    conn.execute('create table if not exists chain_entries(entryhash UNIQUE,chainid,size INT)')


def insert_to_db(conn,entry_hash,chainid,size):
    conn.execute('INSERT OR IGNORE INTO chain_entries(entryhash,chainid,size)  VALUES (?,?,?)',(str(entry_hash),str(chainid),size,))
    #conn.execute('INSERT INTO entries(chainid) SELECT (?) '
                 #'WHERE NOT EXISTS (SELECT chainid FROM entries WHERE chainid = (?))',(str(chainid),str(chainid),))


def commit_to_db(conn):
    conn.commit()

def fetch_from_db(conn):
     result = conn.execute('SELECT * from chain_entries')
     return result

def close_connection_to_db(conn):
    conn.close()
