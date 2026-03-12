import sqlite3

con = sqlite3.connect("bot.db", check_same_thread=False)
cursor = con.cursor()

def init_db():
    con.execute("PRAGMA journal_mode=WAL")
    cursor.execute("""CREATE TABLE IF NOT EXISTS admins (
                        user_id INTENGER PRIMARY KEY,
                        first_name TEXT,
                        username TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS premium (
                        user_id INTENGER PRIMARY KEY,
                        first_name TEXT,
                        username TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS static (
                            user_id INTENGER PRIMARY KEY,
                            send_message INTENGER DEFAULT 0,
                            rec_message INTENGER DEFAULT 0,
                            ref INTENGER DEFAULT 0)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS date(
                        user_id INTENGER PRIMARY KEY,
                        dates DATE)""")
    con.commit()

def add_admin(user_id, first_name, username):
    cursor.execute(
        "INSERT OR REPLACE INTO admins VALUES (?, ?, ?)",
        (user_id, first_name, username)
    )
    con.commit()

def info_admin(user_id):
    cursor.execute("SELECT user_id, first_name, username FROM admins WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def get_all_adm():
    cursor.execute("SELECT * FROM admins")
    return cursor.fetchall()

def get_id_admin():
    cursor.execute("SELECT user_id FROM admins")
    return cursor.fetchone()

def is_admin(user_id):
    cursor.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def del_admin(user_id):
    cursor.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    con.commit()

#премиум пользовтели
def add_premium(user_prem, first_name, username):
    cursor.execute("INSERT OR REPLACE INTO premium VALUES (?, ?, ?)", (user_prem, first_name, username))
    con.commit()

def del_prem(user_id):
    cursor.execute("DELETE FROM premium WHERE user_id =?", (user_id, ))
    con.commit()

def is_prem(user_id):
    cursor.execute("SELECT 1 FROM premium WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def get_premium():
    cursor.execute("SELECT * FROM premium")
    return cursor.fetchall()

def add_date(user_id, date):
    cursor.execute("INSERT OR REPLACE INTO date VALUES (?, ?)", (user_id, date,))
    con.commit()

def get_date(user_id):
    cursor.execute("SELECT dates FROM date WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def data_get(user_id):
    cursor.execute("SELECT dates FROM date WHERE user_id= ?", (user_id,))
    return cursor.fetchone()

#рейтинг
def add_id(user_id):
    cursor.execute("INSERT OR REPLACE INTO static VALUES (?)", (user_id,))
    con.commit()

def add_send_mes(user_id):
    cursor.execute(
        "UPDATE static SET send_message = send_message + 1 WHERE user_id = ?",
        (user_id,)
    )
    if cursor.rowcount== 0:
        cursor.execute("INSERT INTO static (user_id, send_message) VALUES (?, ?)", (user_id, 1))
    con.commit()

def add_rec_mes(user_id):
    cursor.execute("UPDATE static SET rec_message = rec_message + 1 WHERE user_id = ?", (user_id,))
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO static (user_id, rec_message) VALUES (?, 1)", (user_id,))
    con.commit()

def add_ref(user_id):
    cursor.execute("UPDATE static SET ref = ref + 1 WHERE user_id = ?", (user_id,))
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO static (user_id, ref) VALUES (?, 1)",(user_id, ))
    con.commit()

def get_ctatic(idu):
    cursor.execute("SELECT send_message, rec_message, ref FROM static WHERE user_id=? ",(idu,))
    return cursor.fetchone()

def ensure_user_exists(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO static (user_id, send_message, rec_message, ref) VALUES (?, 0, 0, 0)",
        (user_id,))
