import sqlite3
import os # 파일을 다루기 위해 os 모듈을 임포트합니다.

# --- 데이터베이스 파일 이름 ---
DB_FILE = "database.db"

# --- 스크립트 실행 시 기존 DB 파일이 있으면 삭제 ---
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"기존 {DB_FILE} 파일을 삭제했습니다.")

# --- 데이터베이스에 연결 (새 파일 생성) ---
connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

# --- 1. 'prayers' 테이블 만들기 ---
print("'prayers' 테이블을 생성합니다...")
cursor.execute('''
    CREATE TABLE prayers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        pray_count INTEGER NOT NULL DEFAULT 0
    );
''')

# --- 2. 'verses' 테이블 만들기 ---
print("'verses' 테이블을 생성합니다...")
cursor.execute('''
    CREATE TABLE verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL
    );
''')

# --- 'verses' 테이블에 초기 말씀 데이터 추가 ---
print("'verses' 테이블에 초기 데이터를 추가합니다...")
initial_verses = [
    ("너희는 마음에 근심하지 말라 하나님을 믿으니 또 나를 믿으라 (요한복음 14:1)",),
    ("수고하고 무거운 짐 진 자들아 다 내게로 오라 내가 너희를 쉬게 하리라 (마태복음 11:28)",),
    ("아무 것도 염려하지 말고 다만 모든 일에 기도와 간구로, 너희 구할 것을 감사함으로 하나님께 아뢰라 (빌립보서 4:6)",),
    ("주 너의 하나님을 사랑하고 네 이웃을 네 자신 같이 사랑하라 하셨으니 (마가복음 12:30-31)",),
    ("항상 기뻐하라 쉬지 말고 기도하라 범사에 감사하라 (데살로니가전서 5:16-18)",)
]
cursor.executemany('INSERT INTO verses (content) VALUES (?)', initial_verses)

# --- 3. 'qt_notes' 테이블 만들기 ---
print("'qt_notes' 테이블을 생성합니다...")
cursor.execute('''
    CREATE TABLE qt_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
''')

# --- 모든 변경사항 저장하고 연결 닫기 ---
connection.commit()
connection.close()

print(f"\n'{DB_FILE}' 데이터베이스가 성공적으로 초기화되었습니다.")