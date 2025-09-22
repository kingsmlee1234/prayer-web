# app.py
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, g
from datetime import date

app = Flask(__name__)
app.secret_key = 'my-secret-key-1234'
DATABASE = 'database.db'

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

@app.route('/')
def index():
    today_str = date.today().isoformat()
    if 'verse' not in session or session.get('date') != today_str:
        db = get_db()
        verse_record = db.execute('SELECT content FROM verses ORDER BY RANDOM() LIMIT 1').fetchone()
        if verse_record:
            session['verse'] = verse_record['content']
            session['date'] = today_str
        else:
            session['verse'] = "등록된 말씀이 없습니다."
            session['date'] = today_str
            
    db = get_db()
    prayers = db.execute('SELECT * FROM prayers ORDER BY id DESC').fetchall()
    return render_template('index.html', verse=session['verse'], prayers=prayers)

@app.route('/qt', methods=['GET', 'POST'])
def qt_page():
    if request.method == 'POST':
        content = request.form['content']
        share_to_prayers = 'share_to_prayers' in request.form
        
        db = get_db()
        db.execute('INSERT INTO qt_notes (content) VALUES (?)', (content,))
        if share_to_prayers:
            db.execute('INSERT INTO prayers (content) VALUES (?)', (content,))
        db.commit()
            
        return redirect(url_for('index'))
    
    return render_template('qt.html')

@app.route('/prayer', methods=['POST'])
def post_prayer():
    content = request.form['content']
    db = get_db()
    db.execute('INSERT INTO prayers (content) VALUES (?)', (content,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/prayer/<int:prayer_id>/pray', methods=['POST'])
def add_pray_count(prayer_id):
    db = get_db()
    db.execute('UPDATE prayers SET pray_count = pray_count + 1 WHERE id = ?', (prayer_id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)