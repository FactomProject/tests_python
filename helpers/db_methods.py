import sqlite3

def connect_to_db():
    conn = sqlite3.connect('factomd-automation-025k.db')
    return conn

def create_table(conn):
    conn.execute('create table if not exists chain_entries(id UNIQUE,entryhash,chainid,size INT,height INT)')

def create_table_ecblock(conn):
    #conn.execute('create table if not exists ecblock(id UNIQUE,entryhash,credits INT,height INT)')
    conn.execute('create table if not exists ecblock(entryhash,credits INT,height INT)')

def insert_to_db(conn,entry_hash,chainid,size,height):
    conn.execute('INSERT OR IGNORE INTO chain_entries(entryhash,chainid,size,height)  VALUES (?,?,?)',(str(entry_hash),str(chainid),size,height,))


def insert_to_ecblock(conn,entryhash,credits,height):
    conn.execute('INSERT OR IGNORE INTO ecblock(entryhash,credits,height)  VALUES (?,?,?)',(entryhash, credits,height,))

def commit_to_db(conn):
    conn.commit()

def fetch_from_db(conn):
     result = conn.execute('SELECT * from chain_entries')
     return result

def fetch_from_ecblock_db(conn):
    result = conn.execute('SELECT * from ecblock')

def close_connection_to_db(conn):
    conn.close()
