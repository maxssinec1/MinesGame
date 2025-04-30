import sqlite3

conn = None
cursor = None

def _open():
    global conn, cursor
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(''' CREATE TABLE IF NOT EXISTS userData (
            hash STRING NOT NULL,
            userID INTEGER PRIMARY KEY,
            balance INTEGER,
            referalCount INTEGER,
            idYourRef INTEGER)
            ''')
def _close():
    conn.commit()
    cursor.close()

def newUser(HashedID, id, balance, ref):
    _open()
    cursor.execute("INSERT INTO userData (hash, userID, balance, idYourRef) VALUES (?, ?, ?, ?)", ([HashedID, id, balance, ref]))
    _close()

def newUserRef(HashedID, id, balance, ref):
    _open()
    cursor.execute("INSERT INTO userData (hash, userID, balance, idYourRef) VALUES (?, ?, ?, ?)", ([HashedID, id, balance, ref]))
    _close()

def takeUserList():
    _open()
    return str(cursor.execute("SELECT * FROM userData").fetchall())

def takeHashFromID(id):
    _open()
    return str(cursor.execute(f"SELECT hash FROM userData WHERE userID = ?", [(id)]).fetchone()).replace("('", "").replace("',)", "")

def takeAllInfoFromHash(hash):
    _open()
    return cursor.execute(f"SELECT userID, balance FROM userData WHERE hash = ?", hash).fetchall()

def updateBalance(hash, to):
    _open()
    cursor.execute(f"UPDATE userData SET balance = ? WHERE hash = ?", ([to, hash]))
    _close()

def takeBalance(hash):
    _open()
    return cursor.execute(f"SELECT balance FROM userData WHERE hash = ?", ([hash])).fetchall()