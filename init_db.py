# init_db.py
import sqlite3
import os

DB_FILE = "database.db"

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"기존 {DB_FILE} 파일을 삭제했습니다.")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

# --- 1. 'users' 테이블에 'nickname' 컬럼 추가 ---
print("'users' 테이블을 생성합니다...")
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nickname TEXT UNIQUE NOT NULL
    );
''')

# --- 2. 'prayers' 테이블에 작성자 닉네임을 저장할 'author_nickname' 컬럼 추가 ---
print("'prayers' 테이블을 생성합니다...")
cursor.execute('''
    CREATE TABLE prayers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        pray_count INTEGER NOT NULL DEFAULT 0,
        author_nickname TEXT
    );
''')

# --- qt_notes, verses 테이블은 기존과 동일 ---
print("'qt_notes' 테이블을 생성합니다...")
cursor.execute('''
    CREATE TABLE qt_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
''')
print("'verses' 테이블을 생성합니다...")
cursor.execute('''
    CREATE TABLE verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL
    );
''')
initial_verses = [("너희는 마음에 근심하지 말라 하나님을 믿으니 또 나를 믿으라 (요한복음 14:1)",), ("수고하고 무거운 짐 진 자들아 다 내게로 오라 내가 너희를 쉬게 하리라 (마태복음 11:28)",)]
cursor.executemany('INSERT INTO verses (content) VALUES (?)', initial_verses)

connection.commit()
connection.close()
print(f"\n'{DB_FILE}' 데이터베이스가 성공적으로 초기화되었습니다.")