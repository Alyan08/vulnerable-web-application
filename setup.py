import os
import sqlite3
from hashlib import md5


def create_table():
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            city TEXT NOT NULL,
            credit_card TEXT
        );
        """)

        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS set_id AFTER INSERT ON users
        BEGIN
            UPDATE users SET user_id = (SELECT MAX(user_id) + 1 FROM users) WHERE user_id IS NULL;
            UPDATE users SET user_id = 1111 WHERE user_id < 1111;
        END;
        """)

        conn.commit()
        print("Table 'users' created successfully!")
        conn.close()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    finally:
        if conn:
            conn.close()


def user_exists(login):
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE login=?", (login,))
        user = cursor.fetchone()

        conn.close()

        return user is not None

    except:
        return False
    finally:
        if conn:
            conn.close()


def create_user(login, password, role, city, credit_card):
    login = login

    if user_exists(login):
        return {"status": False, "msg": f"user with login {login} already exists"}

    password = password
    hashed_password = md5(password.encode()).hexdigest()
    role = role
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users (login, password, role, city, credit_card)
        VALUES (?, ?, ?, ?, ?);
        """, (login, hashed_password, role, city, credit_card))

        conn.commit()

        return {"status": True, "msg": "user created"}

    except sqlite3.Error as e:
        return {"status": False, "msg": f"error while creating user: {e}"}
    finally:
        if conn:
            conn.close()


def create_base_users():
    create_user("alice", "alice123", "user", "Elista", "2222-2222-2222-2222")
    create_user("bob", "bob123", "user", "Moscow", "3333-3333-3333-3333")
    create_user("john", "john123", "user", "Moscow", "4444-4444-4444-4444")


def create_cloud_folder():
    if not os.path.exists('cloud'):
        os.makedirs('cloud')
