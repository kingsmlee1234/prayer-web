# app.py
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, g
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'my-secret-key-1234'
DATABASE = 'database.db'

# --- DB 연결 관리 ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- 페이지 라우팅 ---

# 🔽 이 함수를 수정했습니다. 🔽
@app.route('/')
def index():
    # 1. 함수가 시작될 때 DB에 먼저 연결합니다.
    db = get_db()
    
    # 2. 오늘의 말씀 로직
    today_str = date.today().isoformat()
    if 'verse' not in session or session.get('date') != today_str:
        verse_record = db.execute('SELECT content FROM verses ORDER BY RANDOM() LIMIT 1').fetchone()
        if verse_record:
            session['verse'] = verse_record['content']
            session['date'] = today_str
        else:
            session['verse'] = "등록된 말씀이 없습니다."
            session['date'] = today_str
            
    # 3. 기도제목 목록 로직
    prayers = db.execute('SELECT * FROM prayers ORDER BY id DESC').fetchall()
    
    # 4. 세션에 저장된 말씀과 DB에서 가져온 기도제목을 함께 전달
    return render_template('index.html', verse=session['verse'], prayers=prayers)

# --- 회원가입 ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        nickname = request.form['nickname']
        password = request.form['password']
        db = get_db()
        error = None

        if not username: error = '사용자 이름이 필요합니다.'
        elif not nickname: error = '닉네임이 필요합니다.'
        elif not password: error = '비밀번호가 필요합니다.'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (username, password, nickname) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), nickname),
                )
                db.commit()
            except db.IntegrityError:
                error = f"사용자 이름 또는 닉네임이 이미 존재합니다."
            else:
                return redirect(url_for("login"))
        
        return render_template('register.html', error=error)
    return render_template('register.html')

# --- 로그인 ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = '잘못된 사용자 이름입니다.'
        elif not check_password_hash(user['password'], password):
            error = '잘못된 비밀번호입니다.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nickname'] = user['nickname']
            return redirect(url_for('index'))
        
        return render_template('login.html', error=error)
    return render_template('login.html')

# --- 로그아웃 ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- QT 노트 작성 ---
@app.route('/qt', methods=['GET', 'POST'])
def qt_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form['content']
        db = get_db()
        db.execute(
            'INSERT INTO qt_notes (content, user_id) VALUES (?, ?)',
            (content, session['user_id'])
        )
        db.commit()
        return redirect(url_for('my_notes'))
    
    return render_template('qt.html')

# --- 나의 QT 노트 목록 ---
@app.route('/my_notes')
def my_notes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    notes = db.execute(
        'SELECT * FROM qt_notes WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    return render_template('my_notes.html', notes=notes)

# --- 기도제목 나누기 ---
@app.route('/prayer', methods=['POST'])
def post_prayer():
    content = request.form['content']
    is_anonymous = 'is_anonymous' in request.form
    author_nickname = None

    if 'user_id' in session and not is_anonymous:
        author_nickname = session['nickname']

    db = get_db()
    db.execute(
        'INSERT INTO prayers (content, author_nickname) VALUES (?, ?)',
        (content, author_nickname)
    )
    db.commit()
    return redirect(url_for('index'))

# --- 기도하기 ---
@app.route('/prayer/<int_prayer_id>/pray', methods=['POST'])
def add_pray_count(prayer_id):
    db = get_db()
    db.execute('UPDATE prayers SET pray_count = pray_count + 1 WHERE id = ?', (prayer_id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)